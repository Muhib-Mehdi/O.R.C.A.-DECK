import customtkinter as ctk
import tkinter.messagebox as messagebox

class SettingsPanel(ctk.CTkFrame):
    def __init__(self, parent, config, authorized_uids, on_save_config, on_save_uids, serial_handler=None, is_locked=False):
        super().__init__(parent)
        self.config = config
        self.authorized_uids = authorized_uids
        self.on_save_config = on_save_config
        self.on_save_uids = on_save_uids
        self.serial_handler = serial_handler
        self.is_locked = is_locked
        
        self.create_ui()
        
    def create_ui(self):
        ctk.CTkLabel(self, text="Settings", font=("Arial", 24, "bold")).pack(pady=20)
        
        sys_frame = ctk.CTkFrame(self)
        sys_frame.pack(fill="x", padx=20, pady=10)
        
        ctk.CTkLabel(sys_frame, text="System Configuration", font=("Arial", 16, "bold")).pack(pady=10)
        
        port_frame = ctk.CTkFrame(sys_frame, fg_color="transparent")
        port_frame.pack(fill="x", padx=20, pady=5)
        ctk.CTkLabel(port_frame, text="COM Port:", width=120, anchor="w").pack(side="left")
        self.port_entry = ctk.CTkEntry(port_frame, width=150)
        self.port_entry.pack(side="left", padx=10)
        self.port_entry.insert(0, self.config.get("com_port", "COM3"))
        
        lock_frame = ctk.CTkFrame(sys_frame, fg_color="transparent")
        lock_frame.pack(fill="x", padx=20, pady=5)
        ctk.CTkLabel(lock_frame, text="Auto-lock (minutes):", width=120, anchor="w").pack(side="left")
        self.autolock_entry = ctk.CTkEntry(lock_frame, width=150)
        self.autolock_entry.pack(side="left", padx=10)
        self.autolock_entry.insert(0, str(self.config.get("auto_lock_minutes", 15)))
        
        if not self.is_locked:
            access_frame = ctk.CTkFrame(self)
            access_frame.pack(fill="x", padx=20, pady=10)
            
            ctk.CTkLabel(access_frame, text="Access Control (Authorized UIDs)", font=("Arial", 16, "bold")).pack(pady=10)
            
            self.uid_listbox = ctk.CTkScrollableFrame(access_frame, height=150)
            self.uid_listbox.pack(fill="x", padx=20, pady=5)
            
            self.refresh_uid_list()
            
            add_frame = ctk.CTkFrame(access_frame, fg_color="transparent")
            add_frame.pack(fill="x", padx=20, pady=10)
            
            self.uid_entry = ctk.CTkEntry(add_frame, placeholder_text="Enter UID (e.g. 52A77A5C)")
            self.uid_entry.pack(side="left", fill="x", expand=True, padx=(0, 10))
            
            ctk.CTkButton(add_frame, text="Add UID", width=100, command=self.add_uid).pack(side="right")
        else:
            locked_frame = ctk.CTkFrame(self, fg_color="#2b2b2b")
            locked_frame.pack(fill="x", padx=20, pady=10)
            
            ctk.CTkLabel(locked_frame, text="🔒 Access Control Settings", font=("Arial", 16, "bold")).pack(pady=10)
            ctk.CTkLabel(locked_frame, text="Unlock the system to manage authorized UIDs", 
                        font=("Arial", 12), text_color="gray").pack(pady=(0, 10))
        
        ctk.CTkButton(self, text="Save Settings", command=self.save_all, fg_color="#2ecc71", hover_color="#27ae60", height=40).pack(pady=30)

    def refresh_uid_list(self):
        if self.is_locked:
            return
            
        for widget in self.uid_listbox.winfo_children():
            widget.destroy()
            
        for uid in self.authorized_uids:
            row = ctk.CTkFrame(self.uid_listbox, fg_color="transparent")
            row.pack(fill="x", pady=2)
            
            ctk.CTkLabel(row, text=uid, anchor="w").pack(side="left", padx=10)
            ctk.CTkButton(row, text="Delete", width=60, fg_color="#c0392b", hover_color="#e74c3c",
                        command=lambda u=uid: self.delete_uid(u)).pack(side="right", padx=10)

    def add_uid(self):
        if self.is_locked:
            return
            
        uid = self.uid_entry.get().strip().upper()
        if not uid: return
        
        if uid in self.authorized_uids:
            messagebox.showwarning("Duplicate", "This UID is already authorized.")
            return
            
        self.authorized_uids.append(uid)
        self.refresh_uid_list()
        self.uid_entry.delete(0, "end")
        self.on_save_uids(self.authorized_uids)

    def delete_uid(self, uid):
        if self.is_locked:
            return
            
        if uid in self.authorized_uids:
            self.authorized_uids.remove(uid)
            self.refresh_uid_list()
            self.on_save_uids(self.authorized_uids)

    def save_all(self):
        new_config = self.config.copy()
        new_config["com_port"] = self.port_entry.get().strip()
        
        try:
            new_config["auto_lock_minutes"] = int(self.autolock_entry.get().strip())
        except ValueError:
            messagebox.showerror("Invalid Input", "Auto-lock must be a number.")
            return
            
        self.on_save_config(new_config)
        
        if not self.is_locked:
            self.on_save_uids(self.authorized_uids)
        
        messagebox.showinfo("Saved", "Settings saved successfully.")

