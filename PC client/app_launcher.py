import customtkinter as ctk
import pyautogui
import time
import subprocess
import os
from tkinter import filedialog
from image_processor import ImageProcessor

class AppLauncher(ctk.CTkFrame):
    def __init__(self, parent, apps_config, mappings, on_save, serial_handler=None):
        super().__init__(parent)
        self.apps_config = apps_config
        self.mappings = mappings
        self.on_save = on_save
        self.serial_handler = serial_handler
        
        self.grid_columnconfigure((0,1,2,3), weight=1)
        
        self.keys = [
            ['A', 'B', 'C', 'D'],
            ['3', '6', '9', '#'],
            ['2', '5', '8', '0'],
            ['1', '4', '7', '*']
        ]
        
        self.create_grid()
        
    def create_grid(self):
        for widget in self.winfo_children():
            widget.destroy()
            
        ctk.CTkLabel(self, text="App Launcher", font=("Arial", 20)).grid(row=0, column=0, columnspan=4, pady=10)
        
        for r in range(4):
            for c in range(4):
                key = self.keys[r][c]
                
                label = self.mappings.get(key, f"App {key}")
                if key == '*': label = "Back"
                
                if key == '*':
                    btn = ctk.CTkButton(
                        self, 
                        text=f"{label}\n({key})",
                        width=120,
                        height=80,
                        fg_color="#444444",
                        state="disabled"
                    )
                else:
                    btn = ctk.CTkButton(
                        self, 
                        text=f"{label}\n({key})",
                        width=120,
                        height=80,
                        command=lambda k=key: self.edit_app(k)
                    )
                btn.grid(row=r+1, column=c, padx=10, pady=10)
                
    def edit_app(self, key):
        dialog = ctk.CTkToplevel(self)
        dialog.title(f"Edit App {key}")
        dialog.geometry("400x350")
        
        dialog.transient(self)
        dialog.grab_set()
        
        current_name = self.mappings.get(key, f"App {key}")
        current_path = self.apps_config.get(key, "")
        
        ctk.CTkLabel(dialog, text=f"Edit App [{key}]", font=("Arial", 16, "bold")).pack(pady=10)
        
        ctk.CTkLabel(dialog, text="Display Name:").pack()
        name_entry = ctk.CTkEntry(dialog, width=250)
        name_entry.pack(pady=5)
        name_entry.insert(0, current_name)
        
        ctk.CTkLabel(dialog, text="App Path or URL:").pack()
        path_entry = ctk.CTkEntry(dialog, width=250)
        path_entry.pack(pady=5)
        path_entry.insert(0, current_path)
        
        def browse():
            file_path = filedialog.askopenfilename(filetypes=[("Executables", "*.exe"), ("All Files", "*.*")])
            if file_path:
                path_entry.delete(0, "end")
                path_entry.insert(0, file_path)
        
        ctk.CTkButton(dialog, text="Browse...", command=browse, width=100).pack(pady=5)
        
        def upload():
            file_path = filedialog.askopenfilename(filetypes=[("Images", "*.png;*.jpg;*.jpeg")])
            if file_path:
                raw_data = ImageProcessor.convert_to_rgb565(file_path)
                if raw_data:
                    if self.serial_handler.send_icon_data(key, raw_data):
                        print(f"Icon sent for key {key}")
                    else:
                        print("Failed to send icon")
                else:
                    print("Failed to convert image")

        ctk.CTkButton(dialog, text="Upload Icon", command=upload, fg_color="#e67e22", hover_color="#d35400").pack(pady=20)
        
        def save():
            new_name = name_entry.get()
            new_path = path_entry.get()
            
            self.mappings[key] = new_name
            
            self.apps_config[key] = new_path
            
            if self.serial_handler and self.serial_handler.serial_conn:
                self.serial_handler.send(f"LABEL_APP:{key}:{new_name}")
            
            self.on_save(self.apps_config, self.mappings)
            
            self.create_grid()
            dialog.destroy()
            
        ctk.CTkButton(dialog, text="Save", command=save).pack(pady=10)

    def launch_app(self, app_name):
        print(f"Launching: {app_name}")
        
        if os.path.exists(app_name):
            try:
                os.startfile(app_name)
                return
            except:
                pass
                
        if app_name.startswith("http"):
            import webbrowser
            webbrowser.open(app_name)
            return
            
        pyautogui.press('win')
        time.sleep(0.1)
        pyautogui.write(app_name)
        time.sleep(0.5)
        pyautogui.press('enter')

    def get_app_for_key(self, key):
        return self.apps_config.get(key, "Unknown")

    def launch_app(self, app_name):
        print(f"Launching: {app_name}")
        
        if os.path.exists(app_name):
            try:
                os.startfile(app_name)
                return
            except:
                pass
                
        if app_name.startswith("http"):
            import webbrowser
            webbrowser.open(app_name)
            return
            
        pyautogui.press('win')
        time.sleep(0.1)
        pyautogui.write(app_name)
        time.sleep(0.5)
        pyautogui.press('enter')

    def get_app_for_key(self, key):
        return self.apps_config.get(key, "Unknown")
