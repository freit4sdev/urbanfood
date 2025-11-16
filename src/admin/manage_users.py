import tkinter as tk
from tkinter import ttk, messagebox
import sqlite3
from src.services.database import get_db


class ManageUsersWindow:
    
    def __init__(self, parent):
        self.parent = parent
        self.window = tk.Toplevel(parent)
        self.window.title("Gerenciar Usuários")
        self.window.geometry("900x600")
        self.window.resizable(True, True)
        self.window.protocol("WM_DELETE_WINDOW", self._on_close)
        
        self._create_widgets()
        self._load_users()
    
    def _create_widgets(self):
        header_frame = tk.Frame(self.window, bg="#2196F3", height=60)
        header_frame.pack(fill="x")
        header_frame.pack_propagate(False)
        
        title_label = tk.Label(
            header_frame,
            text="👥 Gerenciar Usuários",
            font=("Arial", 18, "bold"),
            bg="#2196F3",
            fg="white"
        )
        title_label.pack(pady=15)
        
        content_frame = tk.Frame(self.window)
        content_frame.pack(fill="both", expand=True, padx=20, pady=20)
        
        filter_frame = tk.Frame(content_frame)
        filter_frame.pack(fill="x", pady=(0, 10))
        
        filter_label = tk.Label(filter_frame, text="Filtrar por tipo:", font=("Arial", 10))
        filter_label.pack(side="left", padx=5)
        
        self.filter_var = tk.StringVar(value="Todos")
        filter_combo = ttk.Combobox(
            filter_frame,
            textvariable=self.filter_var,
            values=["Todos", "Cliente", "Loja", "Admin"],
            state="readonly",
            width=15
        )
        filter_combo.pack(side="left", padx=5)
        filter_combo.bind("<<ComboboxSelected>>", lambda e: self._load_users())
        
        refresh_btn = tk.Button(
            filter_frame,
            text="🔄 Atualizar",
            font=("Arial", 11),
            command=self._load_users
        )
        refresh_btn.pack(side="left", padx=5)
        
        tree_frame = tk.Frame(content_frame)
        tree_frame.pack(fill="both", expand=True)
        
        columns = ("ID", "Nome", "Email", "Tipo", "Status", "Bloqueado", "Criado em")
        self.tree = ttk.Treeview(tree_frame, columns=columns, show="headings", height=15)
        
        for col in columns:
            self.tree.heading(col, text=col)
            self.tree.column(col, width=120)
        
        scrollbar = ttk.Scrollbar(tree_frame, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)
        
        self.tree.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        action_frame = tk.Frame(content_frame)
        action_frame.pack(fill="x", pady=10)
        
        block_btn = tk.Button(
            action_frame,
            text="🔒 Bloquear",
            font=("Arial", 10),
            bg="#FF9800",
            fg="white",
            command=self._toggle_block
        )
        block_btn.pack(side="left", padx=5)
        
        activate_btn = tk.Button(
            action_frame,
            text="✅ Ativar",
            font=("Arial", 10),
            bg="#4CAF50",
            fg="white",
            command=self._toggle_active
        )
        activate_btn.pack(side="left", padx=5)
        
        delete_btn = tk.Button(
            action_frame,
            text="🗑️ Excluir",
            font=("Arial", 10),
            bg="#F44336",
            fg="white",
            command=self._delete_user
        )
        delete_btn.pack(side="left", padx=5)
        
        close_btn = tk.Button(
            action_frame,
            text="Fechar",
            font=("Arial", 10),
            command=self._on_close
        )
        close_btn.pack(side="right", padx=5)
    
    def _load_users(self):
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        filter_type = self.filter_var.get()
        type_map = {
            "Todos": None,
            "Cliente": "client",
            "Loja": "store",
            "Admin": "admin"
        }
        
        db = get_db()
        conn = db.get_connection()
        cursor = conn.cursor()
        
        try:
            if type_map[filter_type]:
                cursor.execute("""
                    SELECT id, name, email, user_type, is_active, is_blocked, created_at
                    FROM users
                    WHERE user_type = ?
                    ORDER BY created_at DESC
                """, (type_map[filter_type],))
            else:
                cursor.execute("""
                    SELECT id, name, email, user_type, is_active, is_blocked, created_at
                    FROM users
                    ORDER BY created_at DESC
                """)
            
            users = cursor.fetchall()
            for user in users:
                user_type_map = {
                    "client": "Cliente",
                    "store": "Loja",
                    "admin": "Admin"
                }
                
                status = "Ativo" if user['is_active'] else "Inativo"
                blocked = "Sim" if user['is_blocked'] else "Não"
                
                self.tree.insert("", "end", values=(
                    user['id'],
                    user['name'],
                    user['email'],
                    user_type_map.get(user['user_type'], user['user_type']),
                    status,
                    blocked,
                    user['created_at']
                ), tags=(user['id'],))
        except sqlite3.Error as e:
            messagebox.showerror("Erro", f"Erro ao carregar usuários: {str(e)}")
    
    def _get_selected_user_id(self):
        selected = self.tree.selection()
        if not selected:
            return None
        item = self.tree.item(selected[0])
        return item['tags'][0] if item['tags'] else None
    
    def _toggle_block(self):
        user_id = self._get_selected_user_id()
        if not user_id:
            messagebox.showwarning("Aviso", "Selecione um usuário.")
            return
        
        item = self.tree.selection()[0]
        values = self.tree.item(item)['values']
        is_blocked = values[5] == "Sim"
        
        db = get_db()
        conn = db.get_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute(
                "UPDATE users SET is_blocked = ? WHERE id = ?",
                (0 if is_blocked else 1, user_id)
            )
            conn.commit()
            action = "desbloqueado" if is_blocked else "bloqueado"
            messagebox.showinfo("Sucesso", f"Usuário {action} com sucesso!")
            self._load_users()
        except sqlite3.Error as e:
            messagebox.showerror("Erro", f"Erro ao atualizar usuário: {str(e)}")
    
    def _toggle_active(self):
        user_id = self._get_selected_user_id()
        if not user_id:
            messagebox.showwarning("Aviso", "Selecione um usuário.")
            return
        
        item = self.tree.selection()[0]
        values = self.tree.item(item)['values']
        is_active = values[4] == "Ativo"
        
        db = get_db()
        conn = db.get_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute(
                "UPDATE users SET is_active = ? WHERE id = ?",
                (0 if is_active else 1, user_id)
            )
            conn.commit()
            action = "desativado" if is_active else "ativado"
            messagebox.showinfo("Sucesso", f"Usuário {action} com sucesso!")
            self._load_users()
        except sqlite3.Error as e:
            messagebox.showerror("Erro", f"Erro ao atualizar usuário: {str(e)}")
    
    def _delete_user(self):
        user_id = self._get_selected_user_id()
        if not user_id:
            messagebox.showwarning("Aviso", "Selecione um usuário para excluir.")
            return
        
        item = self.tree.selection()[0]
        values = self.tree.item(item)['values']
        user_name = values[1]
        user_type = values[3]
        
        if user_type == "Admin":
            messagebox.showerror("Erro", "Não é possível excluir usuários administradores.")
            return
        
        if messagebox.askyesno("Confirmar", f"Deseja realmente excluir o usuário '{user_name}'?"):
            db = get_db()
            conn = db.get_connection()
            cursor = conn.cursor()
            
            try:
                cursor.execute("DELETE FROM users WHERE id = ?", (user_id,))
                conn.commit()
                messagebox.showinfo("Sucesso", "Usuário excluído com sucesso!")
                self._load_users()
            except sqlite3.Error as e:
                messagebox.showerror("Erro", f"Erro ao excluir usuário: {str(e)}")
    
    def _on_close(self):
        self.window.destroy()

