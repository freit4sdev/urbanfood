import tkinter as tk
from tkinter import messagebox


class LoginWindow:
    
    def __init__(self, parent):
        self.parent = parent
        self.window = tk.Toplevel(parent)
        self.window.title("UrbanFood - Login")
        self.window.geometry("400x500")
        self.window.resizable(False, False)
        self.window.protocol("WM_DELETE_WINDOW", self._on_close)
        
        self._center_window()
        self._create_widgets()
    
    def _center_window(self):
        self.window.update_idletasks()
        width = self.window.winfo_width()
        height = self.window.winfo_height()
        x = (self.window.winfo_screenwidth() // 2) - (width // 2)
        y = (self.window.winfo_screenheight() // 2) - (height // 2)
        self.window.geometry(f"{width}x{height}+{x}+{y}")
    
    def _create_widgets(self):
        title_label = tk.Label(
            self.window,
            text="🍔 UrbanFood",
            font=("Arial", 24, "bold")
        )
        title_label.pack(pady=30)
        
        subtitle_label = tk.Label(
            self.window,
            text="Sistema de Delivery",
            font=("Arial", 12)
        )
        subtitle_label.pack(pady=5)
        
        type_frame = tk.Frame(self.window)
        type_frame.pack(pady=30)
        
        client_btn = tk.Button(
            type_frame,
            text="👤 Sou Cliente",
            font=("Arial", 12),
            width=20,
            height=2,
            command=self._open_client_login
        )
        client_btn.pack(pady=10)
        
        store_btn = tk.Button(
            type_frame,
            text="🏪 Sou Loja",
            font=("Arial", 12),
            width=20,
            height=2,
            command=self._open_store_login
        )
        store_btn.pack(pady=10)
        
        admin_btn = tk.Button(
            type_frame,
            text="🛠️ Sou Administrador",
            font=("Arial", 12),
            width=20,
            height=2,
            command=self._open_admin_login
        )
        admin_btn.pack(pady=10)
    
    def _open_client_login(self):
        from src.auth.client_auth import ClientAuthWindow
        
        def reopen_main():
            LoginWindow(self.parent)
        
        self.window.destroy()
        ClientAuthWindow(self.parent, on_close_callback=reopen_main)
    
    def _open_store_login(self):
        from src.auth.store_auth import StoreAuthWindow
        
        def reopen_main():
            LoginWindow(self.parent)
        
        self.window.destroy()
        StoreAuthWindow(self.parent, on_close_callback=reopen_main)
    
    def _open_admin_login(self):
        from src.auth.admin_auth import AdminAuthWindow
        
        def reopen_main():
            LoginWindow(self.parent)
        
        self.window.destroy()
        AdminAuthWindow(self.parent, on_close_callback=reopen_main)
    
    def _on_close(self):
        self.window.destroy()
        self.parent.quit()
    
    def destroy(self):
        self.window.destroy()

