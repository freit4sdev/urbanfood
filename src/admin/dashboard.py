import tkinter as tk
from tkinter import messagebox
from src.admin.manage_stores import ManageStoresWindow
from src.admin.manage_users import ManageUsersWindow


class AdminDashboard:
    
    def __init__(self, parent, admin_data):
        self.parent = parent
        self.admin_data = admin_data
        self.window = tk.Toplevel(parent)
        self.window.title("UrbanFood - Painel Administrativo")
        self.window.geometry("600x500")
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
        header_frame = tk.Frame(self.window, bg="#9C27B0", height=80)
        header_frame.pack(fill="x")
        header_frame.pack_propagate(False)
        
        title_label = tk.Label(
            header_frame,
            text="🛠️ Painel Administrativo",
            font=("Arial", 24, "bold"),
            bg="#9C27B0",
            fg="white"
        )
        title_label.pack(pady=20)
        
        welcome_label = tk.Label(
            header_frame,
            text=f"Bem-vindo, {self.admin_data.get('name', 'Administrador')}",
            font=("Arial", 12),
            bg="#9C27B0",
            fg="white"
        )
        welcome_label.pack()
        
        content_frame = tk.Frame(self.window)
        content_frame.pack(fill="both", expand=True, pady=40, padx=40)
        
        stores_btn = tk.Button(
            content_frame,
            text="🏪 Gerenciar Lojas",
            font=("Arial", 14, "bold"),
            bg="#FF9800",
            fg="white",
            width=30,
            height=3,
            command=self._open_manage_stores
        )
        stores_btn.pack(pady=20)
        
        users_btn = tk.Button(
            content_frame,
            text="👥 Gerenciar Usuários",
            font=("Arial", 14, "bold"),
            bg="#2196F3",
            fg="white",
            width=30,
            height=3,
            command=self._open_manage_users
        )
        users_btn.pack(pady=20)
        
        logout_btn = tk.Button(
            content_frame,
            text="Sair",
            font=("Arial", 11),
            width=20,
            height=2,
            command=self._on_close
        )
        logout_btn.pack(pady=20)
    
    def _open_manage_stores(self):
        ManageStoresWindow(self.window)
    
    def _open_manage_users(self):
        ManageUsersWindow(self.window)
    
    def _on_close(self):
        self.window.destroy()
        if self.parent.winfo_exists():
            from src.auth.login import LoginWindow
            LoginWindow(self.parent)
