import customtkinter as ctk
from tkinter import filedialog
import os
from image_processor import ImageProcessor

class PasswordManager(ctk.CTkFrame):
    def __init__(self, parent, passwords, mappings, on_save, serial_handler):
        super().__init__(parent)
        self.passwords = passwords
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
            
        ctk.CTkLabel(self, text="Password Manager", font=("Arial", 20)).grid(row=0, column=0, columnspan=4, pady=10)
        
        for r in range(4):
            for c in range(4):
                key = self.keys[r][c]
                
                label = self.mappings.get(key, f"Item {key}")
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
                        command=lambda k=key: self.edit_password(k)
                    )
                btn.grid(row=r+1, column=c, padx=10, pady=10)

    def edit_password(self, key):
        dialog = ctk.CTkToplevel(self)
        dialog.title(f"Edit Item {key}")
        dialog.geometry("400x450")
        
        dialog.transient(self)
        dialog.grab_set()
        
        current_name = self.mappings.get(key, f"Item {key}")
        current_creds = self.passwords.get(key, {}) 
        if not current_creds:
             current_creds = self.passwords.get(current_name, {})
             
        if not isinstance(current_creds, dict):
             current_creds = {"username": "", "password": current_creds}
             
        ctk.CTkLabel(dialog, text=f"Edit Item [{key}]", font=("Arial", 16, "bold")).pack(pady=10)
        
        ctk.CTkLabel(dialog, text="Display Name:").pack()
        name_entry = ctk.CTkEntry(dialog, width=250)
        name_entry.pack(pady=5)
        name_entry.insert(0, current_name)
        
        ctk.CTkLabel(dialog, text="Username:").pack()
        username_entry = ctk.CTkEntry(dialog, width=250)
        username_entry.pack(pady=5)
        username_entry.insert(0, current_creds.get("username", ""))
        
        ctk.CTkLabel(dialog, text="Password:").pack()
        password_entry = ctk.CTkEntry(dialog, width=250, show="*")
        password_entry.pack(pady=5)
        password_entry.insert(0, current_creds.get("password", ""))
        
        def upload():
            file_path = filedialog.askopenfilename(filetypes=[("Images", "*.png;*.jpg;*.jpeg")])
            if file_path:
                raw_data = ImageProcessor.convert_to_rgb565(file_path)
                if raw_data:
                    if self.serial_handler.send_icon_data(key, raw_data, icon_type="pass"):
                        print(f"Password icon sent for key {key}")
                    else:
                        print("Failed to send icon")
                else:
                    print("Failed to convert image")

        ctk.CTkButton(dialog, text="Upload Icon", command=upload, fg_color="#e67e22", hover_color="#d35400").pack(pady=20)
        
        def save():
            new_name = name_entry.get()
            new_creds = {
                "username": username_entry.get(),
                "password": password_entry.get()
            }
            
            self.mappings[key] = new_name
            
            self.passwords[key] = new_creds
            
            if self.serial_handler and self.serial_handler.serial_conn:
                self.serial_handler.send(f"LABEL_PASS:{key}:{new_name}")
            
            self.on_save(self.passwords, self.mappings)
            
            self.create_grid()
            dialog.destroy()
            
        ctk.CTkButton(dialog, text="Save", command=save).pack(pady=10)
