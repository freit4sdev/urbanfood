import tkinter as tk
from tkinter import messagebox
import re
import sqlite3
from src.services.database import get_db


class StoreSignupWindow:
    
    def __init__(self, parent):
        self.parent = parent
        self.window = tk.Toplevel(parent)
        self.window.title("UrbanFood - Cadastro de Loja")
        self.window.geometry("450x550")
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
            text="🏪 Cadastro de Loja",
            font=("Arial", 20, "bold")
        )
        title_label.pack(pady=20)
        
        form_frame = tk.Frame(self.window)
        form_frame.pack(pady=20, padx=40, fill="both", expand=True)
        
        name_label = tk.Label(
            form_frame,
            text="Nome da Loja:",
            font=("Arial", 10),
            anchor="w"
        )
        name_label.pack(fill="x", pady=(10, 5))
        
        self.name_entry = tk.Entry(
            form_frame,
            font=("Arial", 11),
            width=30
        )
        self.name_entry.pack(fill="x", pady=(0, 10))
        
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
        self.password_entry.pack(fill="x", pady=(0, 10))
        
        confirm_password_label = tk.Label(
            form_frame,
            text="Confirmar Senha:",
            font=("Arial", 10),
            anchor="w"
        )
        confirm_password_label.pack(fill="x", pady=(10, 5))
        
        self.confirm_password_entry = tk.Entry(
            form_frame,
            font=("Arial", 11),
            width=30,
            show="*"
        )
        self.confirm_password_entry.pack(fill="x", pady=(0, 20))
        
        button_frame = tk.Frame(form_frame)
        button_frame.pack(fill="x", pady=10)
        
        signup_btn = tk.Button(
            button_frame,
            text="Cadastrar",
            font=("Arial", 11, "bold"),
            bg="#4CAF50",
            fg="white",
            width=15,
            height=2,
            command=self._handle_signup
        )
        signup_btn.pack(side="left", padx=5)
        
        cancel_btn = tk.Button(
            button_frame,
            text="Cancelar",
            font=("Arial", 11),
            width=15,
            height=2,
            command=self._cancel
        )
        cancel_btn.pack(side="right", padx=5)
        
        self.window.bind("<Return>", lambda e: self._handle_signup())
        self.window.bind("<Escape>", lambda e: self._cancel())
    
    def _validate_email(self, email):
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return re.match(pattern, email) is not None
    
    def _handle_signup(self):
        name = self.name_entry.get().strip()
        email = self.email_entry.get().strip()
        password = self.password_entry.get()
        confirm_password = self.confirm_password_entry.get()
        
        if not name:
            messagebox.showerror("Erro", "Por favor, preencha o nome da loja.")
            return
        
        if not email:
            messagebox.showerror("Erro", "Por favor, preencha o email.")
            return
        
        if not self._validate_email(email):
            messagebox.showerror("Erro", "Por favor, insira um email válido.")
            return
        
        if not password:
            messagebox.showerror("Erro", "Por favor, preencha a senha.")
            return
        
        if len(password) < 6:
            messagebox.showerror("Erro", "A senha deve ter pelo menos 6 caracteres.")
            return
        
        if password != confirm_password:
            messagebox.showerror("Erro", "As senhas não coincidem.")
            return
        
        db = get_db()
        conn = db.get_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute(
                "SELECT id FROM users WHERE email = ?",
                (email,)
            )
            if cursor.fetchone():
                messagebox.showerror("Erro", "Este email já está cadastrado.")
                return
            
            cursor.execute(
                "INSERT INTO users (name, email, password, user_type) VALUES (?, ?, ?, ?)",
                (name, email, password, "store")
            )
            user_id = cursor.lastrowid
            
            cursor.execute(
                "INSERT INTO stores (user_id, name) VALUES (?, ?)",
                (user_id, name)
            )
            
            conn.commit()
            
            messagebox.showinfo("Sucesso", "Loja cadastrada com sucesso!")
            self.window.destroy()
            
        except sqlite3.Error as e:
            messagebox.showerror("Erro", f"Erro ao cadastrar: {str(e)}")
        except Exception as e:
            messagebox.showerror("Erro", f"Erro inesperado: {str(e)}")
    
    def _cancel(self):
        if self.window.winfo_exists():
            self.window.destroy()

