import tkinter as tk
from tkinter import messagebox
import sqlite3
from src.services.database import get_db
from src.auth.store_signup import StoreSignupWindow


class StoreAuthWindow:
    
    def __init__(self, parent, on_close_callback=None):
        self.parent = parent
        self.on_close_callback = on_close_callback
        self.window = tk.Toplevel(parent)
        self.window.title("UrbanFood - Login Loja")
        self.window.geometry("400x400")
        self.window.resizable(False, False)
        self.window.protocol("WM_DELETE_WINDOW", self._cancel)
        
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
            text="🏪 Login Loja",
            font=("Arial", 20, "bold")
        )
        title_label.pack(pady=20)
        
        form_frame = tk.Frame(self.window)
        form_frame.pack(pady=20, padx=40, fill="both", expand=True)
        
        email_label = tk.Label(
            form_frame,
            text="Email:",
            font=("Arial", 10),
            anchor="w"
        )
        email_label.pack(fill="x", pady=(10, 5))
        
        self.email_entry = tk.Entry(
            form_frame,
            font=("Arial", 11),
            width=30
        )
        self.email_entry.pack(fill="x", pady=(0, 10))
        
        password_label = tk.Label(
            form_frame,
            text="Senha:",
            font=("Arial", 10),
            anchor="w"
        )
        password_label.pack(fill="x", pady=(10, 5))
        
        self.password_entry = tk.Entry(
            form_frame,
            font=("Arial", 11),
            width=30,
            show="*"
        )
        self.password_entry.pack(fill="x", pady=(0, 20))
        
        button_frame = tk.Frame(form_frame)
        button_frame.pack(fill="x", pady=10)
        
        login_btn = tk.Button(
            button_frame,
            text="Entrar",
            font=("Arial", 11, "bold"),
            bg="#FF9800",
            fg="white",
            width=15,
            height=2,
            command=self._handle_login
        )
        login_btn.pack(side="left", padx=5)
        
        signup_btn = tk.Button(
            button_frame,
            text="Cadastrar",
            font=("Arial", 11),
            width=15,
            height=2,
            command=self._open_signup
        )
        signup_btn.pack(side="right", padx=5)
        
        signup_link = tk.Label(
            form_frame,
            text="Não tem conta? Clique em Cadastrar",
            font=("Arial", 9),
            fg="blue",
            cursor="hand2"
        )
        signup_link.pack(pady=10)
        signup_link.bind("<Button-1>", lambda e: self._open_signup())
        
        self.window.bind("<Return>", lambda e: self._handle_login())
        self.window.bind("<Escape>", lambda e: self._cancel())
    
    def _handle_login(self):
        email = self.email_entry.get().strip()
        password = self.password_entry.get()
        
        if not email:
            messagebox.showerror("Erro", "Por favor, preencha o email.")
            return
        
        if not password:
            messagebox.showerror("Erro", "Por favor, preencha a senha.")
            return
        
        db = get_db()
        conn = db.get_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute(
                "SELECT id, name, email, user_type, is_active, is_blocked FROM users WHERE email = ? AND password = ? AND user_type = 'store'",
                (email, password)
            )
            user = cursor.fetchone()
            
            if not user:
                messagebox.showerror("Erro", "Email ou senha incorretos.")
                return
            
            if user['is_blocked']:
                messagebox.showerror("Erro", "Sua conta está bloqueada. Entre em contato com o administrador.")
                return
            
            if not user['is_active']:
                messagebox.showerror("Erro", "Sua conta está inativa.")
                return
            
            cursor.execute(
                "SELECT id FROM stores WHERE user_id = ?",
                (user['id'],)
            )
            store = cursor.fetchone()
            
            if not store:
                messagebox.showerror("Erro", "Dados da loja não encontrados.")
                return
            
            self.user_data = dict(user)
            self.store_data = dict(store)
            self._close_window()
            from src.store.dashboard import StoreDashboard
            StoreDashboard(self.parent, self.user_data, self.store_data)
            
        except sqlite3.Error as e:
            messagebox.showerror("Erro", f"Erro ao fazer login: {str(e)}")
        except Exception as e:
            messagebox.showerror("Erro", f"Erro inesperado: {str(e)}")
    
    def _open_signup(self):
        signup_window = StoreSignupWindow(self.window)
    
    def _close_window(self):
        try:
            if self.window.winfo_exists():
                self.window.destroy()
        except:
            pass
        
        if self.on_close_callback:
            try:
                self.on_close_callback()
            except:
                pass
    
    def _cancel(self):
        self._close_window()

