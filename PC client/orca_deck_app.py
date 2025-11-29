import customtkinter as ctk
import threading
import time
import json
import os
import sys
import pyautogui
import pyperclip
from PIL import Image
import pystray
from pystray import MenuItem as item
from serial_handler import SerialHandler
from encryption_manager import EncryptionManager
from security_manager import SecurityManager
from password_manager import PasswordManager
from app_launcher import AppLauncher
from settings_panel import SettingsPanel

ctk.set_appearance_mode("Dark")
ctk.set_default_color_theme("dark-blue")

APP_NAME = "ORCA DECK"

def resource_path(relative_path):
    """ Get absolute path to resource, works for dev and for PyInstaller """
    try:
        # PyInstaller creates a temp folder and stores path in _MEIPASS
        base_path = sys._MEIPASS
    except Exception:
        # In dev, we are in PC client/, assets are in ../assets
        base_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

    return os.path.join(base_path, relative_path)

# Define persistent assets directory
if getattr(sys, 'frozen', False):
    # If running as compiled exe, store data in 'assets' folder next to the executable
    ASSETS_DIR = os.path.join(os.path.dirname(sys.executable), "assets")
else:
    # If running from source, use the project's assets folder
    ASSETS_DIR = resource_path("assets")

# Ensure the directory exists
if not os.path.exists(ASSETS_DIR):
    try:
        os.makedirs(ASSETS_DIR)
    except Exception as e:
        print(f"Error creating assets directory: {e}")

PASSWORDS_FILE = os.path.join(ASSETS_DIR, "passwords.json")
CONFIG_FILE = os.path.join(ASSETS_DIR, "config.json")
APPS_FILE = os.path.join(ASSETS_DIR, "apps.json")
KEY_FILE = os.path.join(ASSETS_DIR, "master.key")
UIDS_FILE = os.path.join(ASSETS_DIR, "authorized_uids.json")
MAPPINGS_FILE = os.path.join(ASSETS_DIR, "mappings.json")

DEFAULT_MAPPINGS = {
    "passwords": {
        "A": "Steam", "B": "Discord", "C": "Valorant", "D": "YouTube",
        "3": "GitHub", "6": "Infinite", "9": "Muhib24", "#": "Brave",
        "2": "Instagram", "5": "LinkedIn", "8": "Other", "0": "Item 12",
        "1": "Item 13", "4": "Item 14", "7": "Item 15", "*": "Back"
    },
    "apps": {
        "A": "Steam", "B": "Settings", "C": "WhatsApp", "D": "Instagram",
        "3": "Discord", "6": "Valorant", "9": "Files", "#": "VS Code",
        "2": "YouTube", "5": "Clock", "8": "Terminal", "0": "OBS",
        "1": "Brave", "4": "GitHub", "7": "Calc", "*": "Back"
    }
}

class OrcaDeckApp(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title(APP_NAME)
        self.geometry("1000x700") 
        self.resizable(True, True)
        
        self.protocol('WM_DELETE_WINDOW', self.quit_app)

        self.is_locked = True
        self.in_rfid_setup = False
        self.encryption_manager = EncryptionManager()
        self.security_manager = SecurityManager(ASSETS_DIR)
        
        # Load encryption key
        if os.path.exists(KEY_FILE):
            self.encryption_manager.load_key_from_file(KEY_FILE)
        
        # Load and decrypt passwords
        self.passwords = {}
        encrypted_passwords = self.load_json(PASSWORDS_FILE)
        if encrypted_passwords:
            try:
                # If it's a dictionary with ciphertext, try to decrypt
                if "ciphertext" in encrypted_passwords:
                    decrypted = self.encryption_manager.decrypt_data(encrypted_passwords)
                    if decrypted:
                        self.passwords = decrypted
                else:
                    # Fallback for legacy plain text (if any)
                    self.passwords = encrypted_passwords
            except Exception as e:
                print(f"Error loading passwords: {e}")

        self.apps_config = self.load_json(APPS_FILE)
        self.config = self.load_json(CONFIG_FILE, {"com_port": "COM3", "auto_lock_minutes": 15})
        self.authorized_uids = self.load_json(UIDS_FILE, [])
        self.mappings = self.load_json(MAPPINGS_FILE, DEFAULT_MAPPINGS)
        
        if "passwords" not in self.mappings: self.mappings["passwords"] = DEFAULT_MAPPINGS["passwords"]
        if "apps" not in self.mappings: self.mappings["apps"] = DEFAULT_MAPPINGS["apps"]
        
        self.serial_handler = SerialHandler(
            port=self.config.get("com_port", "COM3"),
            on_message=self.handle_serial_message
        )
        self.serial_handler.start()

        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        self.font_header = ctk.CTkFont(family="Roboto", size=28, weight="bold")
        self.font_sub = ctk.CTkFont(family="Roboto", size=16)
        self.font_norm = ctk.CTkFont(family="Roboto", size=14)

        self.create_sidebar()
        self.create_main_area()
        
        # Debug: Check security setup status
        setup_status = self.security_manager.is_setup()
        print(f"DEBUG: Security setup status: {setup_status}")
        print(f"DEBUG: Security data file: {self.security_manager.file_path}")
        print(f"DEBUG: Security data content: {self.security_manager.data}")
        
        if not setup_status:
            print("DEBUG: Showing security setup screen")
            self.show_security_setup()
        else:
            print("DEBUG: Showing lock screen")
            self.show_lock_screen()
        
        self.setup_tray()

        self.last_activity = time.time()
        self.check_auto_lock()

    def load_json(self, path, default=None):
        if default is None: default = {}
        if os.path.exists(path):
            try:
                with open(path, 'r') as f:
                    return json.load(f)
            except:
                pass
        return default

    def save_json(self, path, data):
        with open(path, 'w') as f:
            json.dump(data, f, indent=2)

    def create_sidebar(self):
        self.sidebar_frame = ctk.CTkFrame(self, width=220, corner_radius=0, fg_color="#1a1a1a")
        self.sidebar_frame.grid(row=0, column=0, sticky="nsew")
        self.sidebar_frame.grid_rowconfigure(8, weight=1)

        self.logo_label = ctk.CTkLabel(self.sidebar_frame, text=APP_NAME, font=ctk.CTkFont(family="Roboto", size=24, weight="bold"))
        self.logo_label.grid(row=0, column=0, padx=20, pady=(30, 20))

        self.status_label = ctk.CTkLabel(self.sidebar_frame, text="🔴 Disconnected", text_color="#ff5555", font=self.font_norm)
        self.status_label.grid(row=1, column=0, padx=20, pady=(0, 20))

        self.nav_buttons = {}
        btns = [
            ("Dashboard", self.show_dashboard),
            ("Passwords", self.show_passwords),
            ("App Launcher", self.show_apps),
            ("Settings", self.show_settings)
        ]
        
        for i, (text, cmd) in enumerate(btns):
            btn = ctk.CTkButton(
                self.sidebar_frame, 
                text=text, 
                command=cmd, 
                font=self.font_norm,
                fg_color="transparent", 
                hover_color="#333333",
                anchor="w",
                height=40
            )
            btn.grid(row=i+2, column=0, padx=10, pady=5, sticky="ew")
            self.nav_buttons[text] = btn

        self.btn_lock = ctk.CTkButton(
            self.sidebar_frame, 
            text="🔒 Lock System", 
            fg_color="#c0392b", 
            hover_color="#e74c3c",
            command=self.lock_system,
            font=self.font_norm
        )
        self.btn_lock.grid(row=9, column=0, padx=20, pady=30)

    def set_active_nav(self, name):
        for key, btn in self.nav_buttons.items():
            if key == name:
                btn.configure(fg_color="#2c3e50")
            else:
                btn.configure(fg_color="transparent")

    def create_main_area(self):
        self.main_frame = ctk.CTkFrame(self, corner_radius=0, fg_color="#222222")
        self.main_frame.grid(row=0, column=1, sticky="nsew")

    def show_security_setup(self):
        self.clear_main_frame()
        
        container = ctk.CTkFrame(self.main_frame, fg_color="transparent")
        container.place(relx=0.5, rely=0.5, anchor="center")

        ctk.CTkLabel(container, text="Welcome to ORCA DECK", font=self.font_header).pack(pady=10)
        ctk.CTkLabel(container, text="Step 1 of 2", font=self.font_sub, text_color="gray").pack(pady=(0, 10))
        ctk.CTkLabel(container, text="Let's secure your vault.", font=self.font_sub, text_color="gray").pack(pady=(0, 30))
        
        ctk.CTkLabel(container, text="Please answer these 3 security questions.\nThey are your ONLY way back if you lose your RFID card.", font=self.font_norm).pack(pady=10)
        
        questions = self.security_manager.get_questions()
        self.answer_entries = []
        
        for q in questions:
            ctk.CTkLabel(container, text=q, font=ctk.CTkFont(size=12, weight="bold")).pack(pady=(10, 5), anchor="w")
            entry = ctk.CTkEntry(container, width=350, height=35)
            entry.pack(pady=5)
            self.answer_entries.append(entry)
            
        ctk.CTkButton(container, text="Initialize Vault", command=self.save_security_setup, width=200, height=40, font=self.font_norm).pack(pady=30)

    def save_security_setup(self):
        answers = [e.get() for e in self.answer_entries]
        if any(not a for a in answers):
            return
            
        # Save security answers
        self.security_manager.set_answers(answers)
        
        # IMPORTANT: Reload the security manager data to ensure is_setup() returns True
        self.security_manager.data = self.security_manager.load_data()
        
        self.encryption_manager.generate_key()
        self.encryption_manager.save_key_to_file(KEY_FILE)
        
        if os.path.exists(PASSWORDS_FILE):
             try:
                 with open(PASSWORDS_FILE, 'r') as f:
                     old_data = json.load(f)
                 if "encrypted_data" not in old_data:
                     self.passwords = old_data
                     self.save_passwords(self.passwords)
             except:
                 pass
        
        self.show_rfid_setup()

    def show_rfid_setup(self):
        self.clear_main_frame()
        
        container = ctk.CTkFrame(self.main_frame, fg_color="transparent")
        container.place(relx=0.5, rely=0.5, anchor="center")

        ctk.CTkLabel(container, text="🔐 Register Master Card", font=self.font_header).pack(pady=10)
        ctk.CTkLabel(container, text="Step 2 of 2", font=self.font_sub, text_color="gray").pack(pady=(0, 30))
        
        ctk.CTkLabel(container, text="Please scan your RFID card now.\nThis will be your master unlock card.", font=self.font_norm, justify="center").pack(pady=20)
        
        self.rfid_status_label = ctk.CTkLabel(container, text="⏳ Waiting for card scan...", font=ctk.CTkFont(size=14, weight="bold"), text_color="#3498db")
        self.rfid_status_label.pack(pady=20)
        
        self.in_rfid_setup = True

    def complete_setup(self):
        self.is_locked = False
        self.show_dashboard()

    def show_lock_screen(self):
        self.clear_main_frame()
        self.is_locked = True
        self.encryption_manager.clear_key()
        
        lock_frame = ctk.CTkFrame(self.main_frame, fg_color="transparent")
        lock_frame.place(relx=0.5, rely=0.5, anchor="center")

        ctk.CTkLabel(lock_frame, text="🛡️", font=("Arial", 64)).pack(pady=10)
        ctk.CTkLabel(lock_frame, text="System Locked", font=self.font_header).pack(pady=10)
        ctk.CTkLabel(lock_frame, text="Tap your ORCA Card to unlock", font=self.font_sub, text_color="gray").pack(pady=20)
        
        ctk.CTkButton(lock_frame, text="Forgot Card?", command=self.show_security_unlock, fg_color="transparent", border_width=1, text_color="gray").pack(pady=20)

    def show_security_unlock(self):
        self.clear_main_frame()
        
        container = ctk.CTkFrame(self.main_frame, fg_color="transparent")
        container.place(relx=0.5, rely=0.5, anchor="center")

        ctk.CTkLabel(container, text="Security Recovery", font=self.font_header).pack(pady=20)
        
        questions = self.security_manager.get_questions()
        self.unlock_entries = []
        
        for q in questions:
            ctk.CTkLabel(container, text=q, font=ctk.CTkFont(size=12)).pack(pady=(10, 5), anchor="w")
            entry = ctk.CTkEntry(container, width=300)
            entry.pack(pady=5)
            self.unlock_entries.append(entry)
            
        ctk.CTkButton(container, text="Unlock Vault", command=self.verify_security_unlock, width=200, height=40).pack(pady=30)
        ctk.CTkButton(container, text="Back", command=self.show_lock_screen, fg_color="transparent", text_color="gray").pack(pady=5)

    def verify_security_unlock(self):
        answers = [e.get() for e in self.unlock_entries]
        if self.security_manager.verify_answers(answers):
            self.perform_unlock()
        else:
            pass

    def perform_unlock(self):
        if self.encryption_manager.load_key_from_file(KEY_FILE):
            if os.path.exists(PASSWORDS_FILE):
                with open(PASSWORDS_FILE, 'r') as f:
                    data = json.load(f)
                    if "encrypted_data" in data:
                        decrypted = self.encryption_manager.decrypt_data(data)
                        if decrypted:
                            self.passwords = decrypted
            
            self.is_locked = False
            self.show_dashboard()
        else:
            print("Error: Master key file missing or corrupted.")

    def show_dashboard(self):
        if self.is_locked: return
        self.clear_main_frame()
        self.set_active_nav("Dashboard")
        
        ctk.CTkLabel(self.main_frame, text="Dashboard", font=self.font_header).pack(pady=30, padx=40, anchor="w")
        
        cards_frame = ctk.CTkFrame(self.main_frame, fg_color="transparent")
        cards_frame.pack(fill="x", padx=40)
        
        status_card = ctk.CTkFrame(cards_frame, fg_color="#2b2b2b", corner_radius=10)
        status_card.pack(side="left", fill="both", expand=True, padx=(0, 10))
        
        ctk.CTkLabel(status_card, text="System Status", font=ctk.CTkFont(size=16, weight="bold")).pack(pady=15, padx=20, anchor="w")
        
        conn_color = "#2ecc71" if self.serial_handler.connected else "#e74c3c"
        conn_text = "Connected" if self.serial_handler.connected else "Disconnected"
        ctk.CTkLabel(status_card, text=f"• {conn_text}", text_color=conn_color, font=self.font_norm).pack(pady=5, padx=20, anchor="w")
        ctk.CTkLabel(status_card, text=f"• Port: {self.config.get('com_port')}", font=self.font_norm).pack(pady=5, padx=20, anchor="w")
        ctk.CTkLabel(status_card, text=f"• Vault: Unlocked", text_color="#2ecc71", font=self.font_norm).pack(pady=5, padx=20, anchor="w")

        uid_card = ctk.CTkFrame(cards_frame, fg_color="#2b2b2b", corner_radius=10)
        uid_card.pack(side="left", fill="both", expand=True, padx=(10, 0))
        
        ctk.CTkLabel(uid_card, text="Access Control", font=ctk.CTkFont(size=16, weight="bold")).pack(pady=15, padx=20, anchor="w")
        ctk.CTkLabel(uid_card, text=f"{len(self.authorized_uids)} Authorized Cards", font=self.font_norm).pack(pady=5, padx=20, anchor="w")
        
        input_frame = ctk.CTkFrame(uid_card, fg_color="transparent")
        input_frame.pack(pady=10, padx=20, fill="x")
        
        self.uid_entry = ctk.CTkEntry(input_frame, placeholder_text="New UID (e.g. 52A77A5C)", height=35)
        self.uid_entry.pack(side="left", fill="x", expand=True, padx=(0, 10))
        
        ctk.CTkButton(input_frame, text="Add", width=60, height=35, command=self.add_uid).pack(side="right")

    def add_uid(self):
        uid = self.uid_entry.get().strip().upper()
        if uid and uid not in self.authorized_uids:
            self.authorized_uids.append(uid)
            self.save_json(UIDS_FILE, self.authorized_uids)
            self.show_dashboard()
            print(f"Added UID: {uid}")

    def show_passwords(self):
        if self.is_locked: return
        self.clear_main_frame()
        self.set_active_nav("Passwords")
        
        pm = PasswordManager(self.main_frame, self.passwords, self.mappings["passwords"], self.save_passwords, self.serial_handler)
        pm.pack(fill="both", expand=True, padx=20, pady=20)

    def show_apps(self):
        if self.is_locked: return
        self.clear_main_frame()
        self.set_active_nav("App Launcher")
        
        al = AppLauncher(self.main_frame, self.apps_config, self.mappings["apps"], self.save_apps_config, self.serial_handler)
        al.pack(fill="both", expand=True, padx=20, pady=20)

    def show_settings(self):
        self.clear_main_frame()
        self.set_active_nav("Settings")
        
        sp = SettingsPanel(
            self.main_frame, 
            self.config, 
            self.authorized_uids, 
            self.save_config, 
            self.save_uids,
            self.serial_handler,
            self.is_locked
        )
        sp.pack(fill="both", expand=True, padx=20, pady=20)

    def save_uids(self, new_uids):
        self.authorized_uids = new_uids
        self.save_json(UIDS_FILE, self.authorized_uids)
        print(f"Saved {len(new_uids)} UIDs")

    def save_passwords(self, new_passwords, new_mappings=None):
        self.passwords = new_passwords
        encrypted = self.encryption_manager.encrypt_data(self.passwords)
        self.save_json(PASSWORDS_FILE, encrypted)
        
        if new_mappings:
            self.mappings["passwords"] = new_mappings
            self.save_json(MAPPINGS_FILE, self.mappings)

    def save_apps_config(self, new_config, new_mappings=None):
        self.apps_config = new_config
        self.save_json(APPS_FILE, self.apps_config)
        
        if new_mappings:
            self.mappings["apps"] = new_mappings
            self.save_json(MAPPINGS_FILE, self.mappings)

    def save_config(self, new_config):
        self.config = new_config
        self.save_json(CONFIG_FILE, self.config)
        self.serial_handler.stop()
        self.serial_handler = SerialHandler(port=self.config["com_port"], on_message=self.handle_serial_message)
        self.serial_handler.start()

    def clear_main_frame(self):
        for widget in self.main_frame.winfo_children():
            widget.destroy()

    def handle_serial_message(self, message):
        self.after(0, self._process_serial_message, message)

    def _process_serial_message(self, message):
        print(f"Serial: {message}")
        self.last_activity = time.time()
        
        if not self.security_manager.is_setup():
            return

        if self.serial_handler.connected:
             self.status_label.configure(text="🟢 Connected", text_color="#2ecc71")
        else:
             self.status_label.configure(text="🔴 Disconnected", text_color="#ff5555")

        if message == "RFID_UNLOCK_OK":
            if self.is_locked:
                self.perform_unlock()
        
        elif message.startswith("RFID_READ:"):
            try:
                uid = message.split(":")[1].strip().upper()
                print(f"DEBUG: Scanned UID: '{uid}'")
                
                # Handle RFID setup mode
                if self.in_rfid_setup:
                    print(f"DEBUG: RFID Setup - Registering UID: {uid}")
                    self.authorized_uids.append(uid)
                    self.save_json(UIDS_FILE, self.authorized_uids)
                    
                    if hasattr(self, 'rfid_status_label'):
                        self.rfid_status_label.configure(text="✅ Card registered successfully!", text_color="#2ecc71")
                    
                    self.in_rfid_setup = False
                    self.after(1500, self.complete_setup)
                    return
                
                # Normal RFID unlock flow
                print(f"DEBUG: Authorized UIDs: {self.authorized_uids}")
                
                if uid in self.authorized_uids:
                    print("DEBUG: Access Granted. Sending AUTH_OK")
                    self.serial_handler.send("AUTH_OK")
                    if self.is_locked:
                        self.perform_unlock()
                else:
                    print("DEBUG: Access Denied. Sending AUTH_FAIL")
                    self.serial_handler.send("AUTH_FAIL")
            except Exception as e:
                print(f"Error processing RFID: {e}")
                
        elif message.startswith("APP_LAUNCH:"):
            key = message.split(":")[1].strip()
            self.launch_app(key)
            
        elif message.startswith("PASS_LAUNCH:"):
            if not self.is_locked:
                key = message.split(":")[1].strip()
                self.type_password(key)

    def launch_app(self, key):
        app_path = self.apps_config.get(key)
        if not app_path:
            print(f"No app found for key {key}")
            return
            
        print(f"Launching: {app_path}")
        
        if os.path.exists(app_path):
            try:
                os.startfile(app_path)
                return
            except:
                pass
                
        if app_path.startswith("http"):
            import webbrowser
            webbrowser.open(app_path)
            return
            
        # Fallback to typing the name (e.g. for Windows search)
        pyautogui.press('win')
        time.sleep(0.1)
        pyautogui.write(app_path)
        time.sleep(0.5)
        pyautogui.press('enter')


    def type_password(self, key):
        
        creds = self.passwords.get(key)
        if not creds: return
        
        username = creds.get("username", "")
        password = creds.get("password", "")
        
        if username:
            pyautogui.write(username)
            pyautogui.press('tab')
            time.sleep(0.1)
        
        if password:
            pyperclip.copy(password)
            pyautogui.hotkey('ctrl', 'v')
            pyautogui.press('enter')

    def check_auto_lock(self):
        if not self.is_locked:
            elapsed = (time.time() - self.last_activity) / 60
            if elapsed > self.config.get("auto_lock_minutes", 15):
                self.lock_system()
        self.after(5000, self.check_auto_lock)
        
    def lock_system(self):
        self.show_lock_screen()

    def setup_tray(self):
        image = Image.new('RGB', (64, 64), color = (73, 109, 137))
        menu = (item('Show', self.show_window), item('Exit', self.quit_app))
        self.tray_icon = pystray.Icon("name", image, "ORCA DECK", menu)
        threading.Thread(target=self.tray_icon.run, daemon=True).start()

    def show_window(self):
        self.deiconify()
        self.lift()
        
    def hide_window(self):
        self.withdraw()

    def quit_app(self):
        try:
            self.serial_handler.stop()
        except:
            pass
        
        try:
            self.tray_icon.stop()
        except:
            pass
        
        self.quit()
        self.destroy()

    def run(self):
        self.mainloop()

if __name__ == "__main__":
    app = OrcaDeckApp()
    app.run()
