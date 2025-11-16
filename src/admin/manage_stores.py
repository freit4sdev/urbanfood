import tkinter as tk
from tkinter import ttk, messagebox
import sqlite3
import re
from src.services.database import get_db


class ManageStoresWindow:
    
    def __init__(self, parent):
        self.parent = parent
        self.window = tk.Toplevel(parent)
        self.window.title("Gerenciar Lojas")
        self.window.geometry("900x600")
        self.window.resizable(True, True)
        self.window.protocol("WM_DELETE_WINDOW", self._on_close)
        
        self._create_widgets()
        self._load_stores()
    
    def _create_widgets(self):
        header_frame = tk.Frame(self.window, bg="#FF9800", height=60)
        header_frame.pack(fill="x")
        header_frame.pack_propagate(False)
        
        title_label = tk.Label(
            header_frame,
            text="🏪 Gerenciar Lojas",
            font=("Arial", 18, "bold"),
            bg="#FF9800",
            fg="white"
        )
        title_label.pack(pady=15)
        
        content_frame = tk.Frame(self.window)
        content_frame.pack(fill="both", expand=True, padx=20, pady=20)
        
        button_frame = tk.Frame(content_frame)
        button_frame.pack(fill="x", pady=(0, 10))
        
        create_btn = tk.Button(
            button_frame,
            text="➕ Criar Nova Loja",
            font=("Arial", 11, "bold"),
            bg="#4CAF50",
            fg="white",
            command=self._create_store
        )
        create_btn.pack(side="left", padx=5)
        
        refresh_btn = tk.Button(
            button_frame,
            text="🔄 Atualizar",
            font=("Arial", 11),
            command=self._load_stores
        )
        refresh_btn.pack(side="left", padx=5)
        
        tree_frame = tk.Frame(content_frame)
        tree_frame.pack(fill="both", expand=True)
        
        columns = ("ID", "Nome", "Email", "Descrição", "Criado em")
        self.tree = ttk.Treeview(tree_frame, columns=columns, show="headings", height=15)
        
        for col in columns:
            self.tree.heading(col, text=col)
            self.tree.column(col, width=150)
        
        scrollbar = ttk.Scrollbar(tree_frame, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)
        
        self.tree.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        action_frame = tk.Frame(content_frame)
        action_frame.pack(fill="x", pady=10)
        
        edit_btn = tk.Button(
            action_frame,
            text="✏️ Editar",
            font=("Arial", 10),
            bg="#2196F3",
            fg="white",
            command=self._edit_store
        )
        edit_btn.pack(side="left", padx=5)
        
        delete_btn = tk.Button(
            action_frame,
            text="🗑️ Excluir",
            font=("Arial", 10),
            bg="#F44336",
            fg="white",
            command=self._delete_store
        )
        delete_btn.pack(side="left", padx=5)
        
        close_btn = tk.Button(
            action_frame,
            text="Fechar",
            font=("Arial", 10),
            command=self._on_close
        )
        close_btn.pack(side="right", padx=5)
    
    def _load_stores(self):
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        db = get_db()
        conn = db.get_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute("""
                SELECT s.id, s.name, u.email, s.description, s.created_at, u.id as user_id
                FROM stores s
                JOIN users u ON s.user_id = u.id
                ORDER BY s.created_at DESC
            """)
            
            stores = cursor.fetchall()
            for store in stores:
                self.tree.insert("", "end", values=(
                    store['id'],
                    store['name'],
                    store['email'],
                    store['description'] or "",
                    store['created_at']
                ), tags=(store['user_id'],))
        except sqlite3.Error as e:
            messagebox.showerror("Erro", f"Erro ao carregar lojas: {str(e)}")
    
    def _create_store(self):
        CreateStoreWindow(self.window, callback=self._load_stores)
    
    def _edit_store(self):
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("Aviso", "Selecione uma loja para editar.")
            return
        
        item = self.tree.item(selected[0])
        store_id = item['values'][0]
        user_id = self.tree.item(selected[0])['tags'][0]
        
        EditStoreWindow(self.window, store_id, user_id, callback=self._load_stores)
    
    def _delete_store(self):
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("Aviso", "Selecione uma loja para excluir.")
            return
        
        item = self.tree.item(selected[0])
        store_id = item['values'][0]
        store_name = item['values'][1]
        user_id = self.tree.item(selected[0])['tags'][0]
        
        if messagebox.askyesno("Confirmar", f"Deseja realmente excluir a loja '{store_name}'?"):
            db = get_db()
            conn = db.get_connection()
            cursor = conn.cursor()
            
            try:
                cursor.execute("DELETE FROM users WHERE id = ?", (user_id,))
                conn.commit()
                messagebox.showinfo("Sucesso", "Loja excluída com sucesso!")
                self._load_stores()
            except sqlite3.Error as e:
                messagebox.showerror("Erro", f"Erro ao excluir loja: {str(e)}")
    
    def _on_close(self):
        self.window.destroy()


class CreateStoreWindow:
    
    def __init__(self, parent, callback=None):
        self.parent = parent
        self.callback = callback
        self.window = tk.Toplevel(parent)
        self.window.title("Criar Nova Loja")
        self.window.geometry("450x500")
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
            text="➕ Criar Nova Loja",
            font=("Arial", 18, "bold")
        )
        title_label.pack(pady=20)
        
        form_frame = tk.Frame(self.window)
        form_frame.pack(pady=20, padx=40, fill="both", expand=True)
        
        name_label = tk.Label(form_frame, text="Nome da Loja:", font=("Arial", 10), anchor="w")
        name_label.pack(fill="x", pady=(10, 5))
        self.name_entry = tk.Entry(form_frame, font=("Arial", 11), width=30)
        self.name_entry.pack(fill="x", pady=(0, 10))
        
        email_label = tk.Label(form_frame, text="Email:", font=("Arial", 10), anchor="w")
        email_label.pack(fill="x", pady=(10, 5))
        self.email_entry = tk.Entry(form_frame, font=("Arial", 11), width=30)
        self.email_entry.pack(fill="x", pady=(0, 10))
        
        password_label = tk.Label(form_frame, text="Senha:", font=("Arial", 10), anchor="w")
        password_label.pack(fill="x", pady=(10, 5))
        self.password_entry = tk.Entry(form_frame, font=("Arial", 11), width=30, show="*")
        self.password_entry.pack(fill="x", pady=(0, 10))
        
        description_label = tk.Label(form_frame, text="Descrição:", font=("Arial", 10), anchor="w")
        description_label.pack(fill="x", pady=(10, 5))
        self.description_text = tk.Text(form_frame, font=("Arial", 11), width=30, height=4)
        self.description_text.pack(fill="x", pady=(0, 20))
        
        button_frame = tk.Frame(form_frame)
        button_frame.pack(fill="x", pady=10)
        
        create_btn = tk.Button(
            button_frame,
            text="Criar",
            font=("Arial", 11, "bold"),
            bg="#4CAF50",
            fg="white",
            width=15,
            height=2,
            command=self._handle_create
        )
        create_btn.pack(side="left", padx=5)
        
        cancel_btn = tk.Button(
            button_frame,
            text="Cancelar",
            font=("Arial", 11),
            width=15,
            height=2,
            command=self._cancel
        )
        cancel_btn.pack(side="right", padx=5)
    
    def _validate_email(self, email):
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return re.match(pattern, email) is not None
    
    def _handle_create(self):
        name = self.name_entry.get().strip()
        email = self.email_entry.get().strip()
        password = self.password_entry.get()
        description = self.description_text.get("1.0", "end-1c").strip()
        
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
        
        db = get_db()
        conn = db.get_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute("SELECT id FROM users WHERE email = ?", (email,))
            if cursor.fetchone():
                messagebox.showerror("Erro", "Este email já está cadastrado.")
                return
            
            cursor.execute(
                "INSERT INTO users (name, email, password, user_type) VALUES (?, ?, ?, ?)",
                (name, email, password, "store")
            )
            user_id = cursor.lastrowid
            
            cursor.execute(
                "INSERT INTO stores (user_id, name, description) VALUES (?, ?, ?)",
                (user_id, name, description if description else None)
            )
            
            conn.commit()
            messagebox.showinfo("Sucesso", "Loja criada com sucesso!")
            self.window.destroy()
            if self.callback:
                self.callback()
        except sqlite3.Error as e:
            messagebox.showerror("Erro", f"Erro ao criar loja: {str(e)}")
    
    def _cancel(self):
        self.window.destroy()


class EditStoreWindow:
    
    def __init__(self, parent, store_id, user_id, callback=None):
        self.parent = parent
        self.store_id = store_id
        self.user_id = user_id
        self.callback = callback
        self.window = tk.Toplevel(parent)
        self.window.title("Editar Loja")
        self.window.geometry("450x500")
        self.window.resizable(False, False)
        self.window.protocol("WM_DELETE_WINDOW", self._cancel)
        
        self._center_window()
        self._load_data()
        self._create_widgets()
    
    def _center_window(self):
        self.window.update_idletasks()
        width = self.window.winfo_width()
        height = self.window.winfo_height()
        x = (self.window.winfo_screenwidth() // 2) - (width // 2)
        y = (self.window.winfo_screenheight() // 2) - (height // 2)
        self.window.geometry(f"{width}x{height}+{x}+{y}")
    
    def _load_data(self):
        db = get_db()
        conn = db.get_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT s.name, s.description, u.email
            FROM stores s
            JOIN users u ON s.user_id = u.id
            WHERE s.id = ?
        """, (self.store_id,))
        
        self.store_data = cursor.fetchone()
    
    def _create_widgets(self):
        title_label = tk.Label(
            self.window,
            text="✏️ Editar Loja",
            font=("Arial", 18, "bold")
        )
        title_label.pack(pady=20)
        
        form_frame = tk.Frame(self.window)
        form_frame.pack(pady=20, padx=40, fill="both", expand=True)
        
        name_label = tk.Label(form_frame, text="Nome da Loja:", font=("Arial", 10), anchor="w")
        name_label.pack(fill="x", pady=(10, 5))
        self.name_entry = tk.Entry(form_frame, font=("Arial", 11), width=30)
        self.name_entry.insert(0, self.store_data['name'])
        self.name_entry.pack(fill="x", pady=(0, 10))
        
        email_label = tk.Label(form_frame, text="Email:", font=("Arial", 10), anchor="w")
        email_label.pack(fill="x", pady=(10, 5))
        self.email_entry = tk.Entry(form_frame, font=("Arial", 11), width=30)
        self.email_entry.insert(0, self.store_data['email'])
        self.email_entry.pack(fill="x", pady=(0, 10))
        
        password_label = tk.Label(form_frame, text="Nova Senha (deixe em branco para manter):", font=("Arial", 10), anchor="w")
        password_label.pack(fill="x", pady=(10, 5))
        self.password_entry = tk.Entry(form_frame, font=("Arial", 11), width=30, show="*")
        self.password_entry.pack(fill="x", pady=(0, 10))
        
        description_label = tk.Label(form_frame, text="Descrição:", font=("Arial", 10), anchor="w")
        description_label.pack(fill="x", pady=(10, 5))
        self.description_text = tk.Text(form_frame, font=("Arial", 11), width=30, height=4)
        self.description_text.insert("1.0", self.store_data['description'] or "")
        self.description_text.pack(fill="x", pady=(0, 20))
        
        button_frame = tk.Frame(form_frame)
        button_frame.pack(fill="x", pady=10)
        
        save_btn = tk.Button(
            button_frame,
            text="Salvar",
            font=("Arial", 11, "bold"),
            bg="#4CAF50",
            fg="white",
            width=15,
            height=2,
            command=self._handle_save
        )
        save_btn.pack(side="left", padx=5)
        
        cancel_btn = tk.Button(
            button_frame,
            text="Cancelar",
            font=("Arial", 11),
            width=15,
            height=2,
            command=self._cancel
        )
        cancel_btn.pack(side="right", padx=5)
    
    def _handle_save(self):
        name = self.name_entry.get().strip()
        email = self.email_entry.get().strip()
        password = self.password_entry.get()
        description = self.description_text.get("1.0", "end-1c").strip()
        
        if not name:
            messagebox.showerror("Erro", "Por favor, preencha o nome da loja.")
            return
        
        if not email:
            messagebox.showerror("Erro", "Por favor, preencha o email.")
            return
        
        db = get_db()
        conn = db.get_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute("SELECT id FROM users WHERE email = ? AND id != ?", (email, self.user_id))
            if cursor.fetchone():
                messagebox.showerror("Erro", "Este email já está cadastrado.")
                return
            
            cursor.execute(
                "UPDATE users SET name = ?, email = ? WHERE id = ?",
                (name, email, self.user_id)
            )
            
            if password:
                if len(password) < 6:
                    messagebox.showerror("Erro", "A senha deve ter pelo menos 6 caracteres.")
                    return
                cursor.execute(
                    "UPDATE users SET password = ? WHERE id = ?",
                    (password, self.user_id)
                )
            
            cursor.execute(
                "UPDATE stores SET name = ?, description = ? WHERE id = ?",
                (name, description if description else None, self.store_id)
            )
            
            conn.commit()
            messagebox.showinfo("Sucesso", "Loja atualizada com sucesso!")
            self.window.destroy()
            if self.callback:
                self.callback()
        except sqlite3.Error as e:
            messagebox.showerror("Erro", f"Erro ao atualizar loja: {str(e)}")
    
    def _cancel(self):
        self.window.destroy()

