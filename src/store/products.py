import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import sqlite3
from pathlib import Path
from src.services.database import get_db


class StoreProductsPage:
    
    def __init__(self, parent, user_data, store_data, dashboard_ref=None):
        self.parent = parent
        self.user_data = user_data
        self.store_data = store_data
        self.dashboard_ref = dashboard_ref
        
        self._create_widgets()
        self._load_products()
    
    def _create_widgets(self):
        header_frame = tk.Frame(self.parent, bg="#FF9800", height=80)
        header_frame.pack(fill="x")
        header_frame.pack_propagate(False)
        
        title_frame = tk.Frame(header_frame, bg="#FF9800")
        title_frame.pack(fill="x", padx=20, pady=10)
        
        title_label = tk.Label(
            title_frame,
            text="🍔 Meus Produtos",
            font=("Arial", 24, "bold"),
            bg="#FF9800",
            fg="white"
        )
        title_label.pack(side="left")
        
        add_btn = tk.Button(
            title_frame,
            text="➕ Adicionar Produto",
            font=("Arial", 11, "bold"),
            bg="#4CAF50",
            fg="white",
            command=self._open_add_product
        )
        add_btn.pack(side="right", padx=10)
        
        main_frame = tk.Frame(self.parent)
        main_frame.pack(fill="both", expand=True, padx=20, pady=20)
        
        canvas = tk.Canvas(main_frame, bg="white")
        scrollbar = ttk.Scrollbar(main_frame, orient="vertical", command=canvas.yview)
        scrollable_frame = tk.Frame(canvas, bg="white")
        
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        self.products_frame = scrollable_frame
    
    def _load_products(self):
        for widget in self.products_frame.winfo_children():
            widget.destroy()
        
        db = get_db()
        conn = db.get_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute("""
                SELECT id, name, description, price, image_path, is_available
                FROM products
                WHERE store_id = ?
                ORDER BY created_at DESC
            """, (self.store_data['id'],))
            
            products = cursor.fetchall()
            
            if not products:
                no_products_label = tk.Label(
                    self.products_frame,
                    text="Nenhum produto cadastrado ainda.\nClique em 'Adicionar Produto' para começar.",
                    font=("Arial", 14),
                    bg="white",
                    fg="#757575"
                )
                no_products_label.pack(pady=50)
                return
            
            for product in products:
                product_frame = tk.Frame(self.products_frame, bg="white", relief="solid", bd=2)
                product_frame.pack(fill="x", padx=10, pady=10)
                
                product_content = tk.Frame(product_frame, bg="white")
                product_content.pack(fill="x", padx=15, pady=10)
                
                name_label = tk.Label(
                    product_content,
                    text=product['name'],
                    font=("Arial", 16, "bold"),
                    bg="white",
                    anchor="w"
                )
                name_label.pack(fill="x", pady=(0, 5))
                
                if product['description']:
                    desc_label = tk.Label(
                        product_content,
                        text=product['description'],
                        font=("Arial", 10),
                        bg="white",
                        anchor="w",
                        wraplength=600,
                        fg="#424242"
                    )
                    desc_label.pack(fill="x", pady=(0, 5))
                
                bottom_frame = tk.Frame(product_content, bg="white")
                bottom_frame.pack(fill="x")
                
                price_label = tk.Label(
                    bottom_frame,
                    text=f"R$ {product['price']:.2f}",
                    font=("Arial", 14, "bold"),
                    bg="white",
                    fg="#4CAF50"
                )
                price_label.pack(side="left")
                
                status_label = tk.Label(
                    bottom_frame,
                    text="Disponível" if product['is_available'] else "Indisponível",
                    font=("Arial", 10),
                    bg="white",
                    fg="#4CAF50" if product['is_available'] else "#F44336"
                )
                status_label.pack(side="left", padx=20)
                
                buttons_frame = tk.Frame(bottom_frame, bg="white")
                buttons_frame.pack(side="right")
                
                edit_btn = tk.Button(
                    buttons_frame,
                    text="✏️ Editar",
                    font=("Arial", 9),
                    bg="#2196F3",
                    fg="white",
                    command=lambda pid=product['id']: self._open_edit_product(pid)
                )
                edit_btn.pack(side="left", padx=2)
                
                toggle_btn = tk.Button(
                    buttons_frame,
                    text="✅ Disponível" if not product['is_available'] else "❌ Indisponível",
                    font=("Arial", 9),
                    bg="#FF9800" if product['is_available'] else "#4CAF50",
                    fg="white",
                    command=lambda pid=product['id'], avail=product['is_available']: self._toggle_availability(pid, avail)
                )
                toggle_btn.pack(side="left", padx=2)
                
                delete_btn = tk.Button(
                    buttons_frame,
                    text="🗑️ Excluir",
                    font=("Arial", 9),
                    bg="#F44336",
                    fg="white",
                    command=lambda pid=product['id']: self._delete_product(pid)
                )
                delete_btn.pack(side="left", padx=2)
        
        except sqlite3.Error as e:
            messagebox.showerror("Erro", f"Erro ao carregar produtos: {str(e)}")
    
    def _open_add_product(self):
        AddProductWindow(self.parent.winfo_toplevel(), self.store_data, self)
    
    def _open_edit_product(self, product_id):
        EditProductWindow(self.parent.winfo_toplevel(), self.store_data, product_id, self)
    
    def _toggle_availability(self, product_id, current_status):
        db = get_db()
        conn = db.get_connection()
        cursor = conn.cursor()
        
        try:
            new_status = 0 if current_status else 1
            cursor.execute("""
                UPDATE products 
                SET is_available = ?
                WHERE id = ? AND store_id = ?
            """, (new_status, product_id, self.store_data['id']))
            
            conn.commit()
            messagebox.showinfo("Sucesso", "Status do produto atualizado!")
            self._load_products()
        
        except sqlite3.Error as e:
            messagebox.showerror("Erro", f"Erro ao atualizar produto: {str(e)}")
    
    def _delete_product(self, product_id):
        if not messagebox.askyesno("Confirmar", "Tem certeza que deseja excluir este produto?"):
            return
        
        db = get_db()
        conn = db.get_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute("""
                DELETE FROM products 
                WHERE id = ? AND store_id = ?
            """, (product_id, self.store_data['id']))
            
            conn.commit()
            messagebox.showinfo("Sucesso", "Produto excluído com sucesso!")
            self._load_products()
        
        except sqlite3.Error as e:
            messagebox.showerror("Erro", f"Erro ao excluir produto: {str(e)}")


class AddProductWindow:
    
    def __init__(self, parent, store_data, products_page_ref):
        self.parent = parent
        self.store_data = store_data
        self.products_page_ref = products_page_ref
        
        self.window = tk.Toplevel(parent)
        self.window.title("Adicionar Produto")
        self.window.geometry("500x500")
        self.window.resizable(False, False)
        self.window.protocol("WM_DELETE_WINDOW", self._cancel)
        
        self.image_path = None
        self._create_widgets()
        self._center_window()
    
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
            text="➕ Adicionar Produto",
            font=("Arial", 18, "bold")
        )
        title_label.pack(pady=20)
        
        form_frame = tk.Frame(self.window)
        form_frame.pack(pady=20, padx=40, fill="both", expand=True)
        
        name_label = tk.Label(form_frame, text="Nome:", font=("Arial", 10), anchor="w")
        name_label.pack(fill="x", pady=(10, 5))
        
        self.name_entry = tk.Entry(form_frame, font=("Arial", 11), width=30)
        self.name_entry.pack(fill="x", pady=(0, 10))
        
        desc_label = tk.Label(form_frame, text="Descrição:", font=("Arial", 10), anchor="w")
        desc_label.pack(fill="x", pady=(10, 5))
        
        self.desc_text = tk.Text(form_frame, font=("Arial", 11), width=30, height=4)
        self.desc_text.pack(fill="x", pady=(0, 10))
        
        price_label = tk.Label(form_frame, text="Preço (R$):", font=("Arial", 10), anchor="w")
        price_label.pack(fill="x", pady=(10, 5))
        
        self.price_entry = tk.Entry(form_frame, font=("Arial", 11), width=30)
        self.price_entry.pack(fill="x", pady=(0, 10))
        
        image_btn = tk.Button(
            form_frame,
            text="📷 Selecionar Imagem",
            font=("Arial", 10),
            command=self._select_image
        )
        image_btn.pack(pady=10)
        
        self.image_label = tk.Label(
            form_frame,
            text="Nenhuma imagem selecionada",
            font=("Arial", 9),
            fg="#757575"
        )
        self.image_label.pack()
        
        button_frame = tk.Frame(form_frame)
        button_frame.pack(pady=20)
        
        save_btn = tk.Button(
            button_frame,
            text="Salvar",
            font=("Arial", 11, "bold"),
            bg="#4CAF50",
            fg="white",
            width=15,
            command=self._save_product
        )
        save_btn.pack(side="left", padx=5)
        
        cancel_btn = tk.Button(
            button_frame,
            text="Cancelar",
            font=("Arial", 11),
            width=15,
            command=self._cancel
        )
        cancel_btn.pack(side="left", padx=5)
    
    def _select_image(self):
        file_path = filedialog.askopenfilename(
            title="Selecionar Imagem",
            filetypes=[("Imagens", "*.png *.jpg *.jpeg *.gif *.bmp")]
        )
        if file_path:
            self.image_path = file_path
            self.image_label.config(text=f"Imagem: {Path(file_path).name}")
    
    def _save_product(self):
        name = self.name_entry.get().strip()
        description = self.desc_text.get("1.0", tk.END).strip()
        price_str = self.price_entry.get().strip()
        
        if not name:
            messagebox.showerror("Erro", "Por favor, preencha o nome do produto.")
            return
        
        if not price_str:
            messagebox.showerror("Erro", "Por favor, preencha o preço.")
            return
        
        try:
            price = float(price_str)
            if price <= 0:
                raise ValueError
        except ValueError:
            messagebox.showerror("Erro", "Por favor, insira um preço válido.")
            return
        
        db = get_db()
        conn = db.get_connection()
        cursor = conn.cursor()
        
        try:
            image_path_db = None
            if self.image_path:
                products_dir = Path(__file__).parent.parent.parent / "assets" / "products"
                products_dir.mkdir(parents=True, exist_ok=True)
                
                import shutil
                file_ext = Path(self.image_path).suffix
                new_filename = f"{self.store_data['id']}_{name.replace(' ', '_')}{file_ext}"
                new_path = products_dir / new_filename
                shutil.copy2(self.image_path, new_path)
                image_path_db = str(new_path)
            
            cursor.execute("""
                INSERT INTO products (store_id, name, description, price, image_path)
                VALUES (?, ?, ?, ?, ?)
            """, (self.store_data['id'], name, description if description else None, price, image_path_db))
            
            conn.commit()
            messagebox.showinfo("Sucesso", "Produto adicionado com sucesso!")
            self.window.destroy()
            if self.products_page_ref:
                self.products_page_ref._load_products()
        
        except sqlite3.Error as e:
            messagebox.showerror("Erro", f"Erro ao salvar produto: {str(e)}")
        except Exception as e:
            messagebox.showerror("Erro", f"Erro inesperado: {str(e)}")
    
    def _cancel(self):
        self.window.destroy()


class EditProductWindow:
    
    def __init__(self, parent, store_data, product_id, products_page_ref):
        self.parent = parent
        self.store_data = store_data
        self.product_id = product_id
        self.products_page_ref = products_page_ref
        
        self.window = tk.Toplevel(parent)
        self.window.title("Editar Produto")
        self.window.geometry("500x500")
        self.window.resizable(False, False)
        self.window.protocol("WM_DELETE_WINDOW", self._cancel)
        
        self.image_path = None
        self._load_product_data()
        self._create_widgets()
        self._center_window()
    
    def _center_window(self):
        self.window.update_idletasks()
        width = self.window.winfo_width()
        height = self.window.winfo_height()
        x = (self.window.winfo_screenwidth() // 2) - (width // 2)
        y = (self.window.winfo_screenheight() // 2) - (height // 2)
        self.window.geometry(f"{width}x{height}+{x}+{y}")
    
    def _load_product_data(self):
        db = get_db()
        conn = db.get_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT name, description, price, image_path
            FROM products
            WHERE id = ? AND store_id = ?
        """, (self.product_id, self.store_data['id']))
        
        product = cursor.fetchone()
        if product:
            self.product_data = dict(product)
        else:
            messagebox.showerror("Erro", "Produto não encontrado.")
            self.window.destroy()
    
    def _create_widgets(self):
        title_label = tk.Label(
            self.window,
            text="✏️ Editar Produto",
            font=("Arial", 18, "bold")
        )
        title_label.pack(pady=20)
        
        form_frame = tk.Frame(self.window)
        form_frame.pack(pady=20, padx=40, fill="both", expand=True)
        
        name_label = tk.Label(form_frame, text="Nome:", font=("Arial", 10), anchor="w")
        name_label.pack(fill="x", pady=(10, 5))
        
        self.name_entry = tk.Entry(form_frame, font=("Arial", 11), width=30)
        self.name_entry.insert(0, self.product_data.get('name', ''))
        self.name_entry.pack(fill="x", pady=(0, 10))
        
        desc_label = tk.Label(form_frame, text="Descrição:", font=("Arial", 10), anchor="w")
        desc_label.pack(fill="x", pady=(10, 5))
        
        self.desc_text = tk.Text(form_frame, font=("Arial", 11), width=30, height=4)
        self.desc_text.insert("1.0", self.product_data.get('description', ''))
        self.desc_text.pack(fill="x", pady=(0, 10))
        
        price_label = tk.Label(form_frame, text="Preço (R$):", font=("Arial", 10), anchor="w")
        price_label.pack(fill="x", pady=(10, 5))
        
        self.price_entry = tk.Entry(form_frame, font=("Arial", 11), width=30)
        self.price_entry.insert(0, str(self.product_data.get('price', '')))
        self.price_entry.pack(fill="x", pady=(0, 10))
        
        image_btn = tk.Button(
            form_frame,
            text="📷 Selecionar Nova Imagem",
            font=("Arial", 10),
            command=self._select_image
        )
        image_btn.pack(pady=10)
        
        current_image = self.product_data.get('image_path', '')
        image_text = f"Imagem atual: {Path(current_image).name}" if current_image else "Nenhuma imagem"
        self.image_label = tk.Label(
            form_frame,
            text=image_text,
            font=("Arial", 9),
            fg="#757575"
        )
        self.image_label.pack()
        
        button_frame = tk.Frame(form_frame)
        button_frame.pack(pady=20)
        
        save_btn = tk.Button(
            button_frame,
            text="Salvar",
            font=("Arial", 11, "bold"),
            bg="#4CAF50",
            fg="white",
            width=15,
            command=self._save_product
        )
        save_btn.pack(side="left", padx=5)
        
        cancel_btn = tk.Button(
            button_frame,
            text="Cancelar",
            font=("Arial", 11),
            width=15,
            command=self._cancel
        )
        cancel_btn.pack(side="left", padx=5)
    
    def _select_image(self):
        file_path = filedialog.askopenfilename(
            title="Selecionar Imagem",
            filetypes=[("Imagens", "*.png *.jpg *.jpeg *.gif *.bmp")]
        )
        if file_path:
            self.image_path = file_path
            self.image_label.config(text=f"Nova imagem: {Path(file_path).name}")
    
    def _save_product(self):
        name = self.name_entry.get().strip()
        description = self.desc_text.get("1.0", tk.END).strip()
        price_str = self.price_entry.get().strip()
        
        if not name:
            messagebox.showerror("Erro", "Por favor, preencha o nome do produto.")
            return
        
        if not price_str:
            messagebox.showerror("Erro", "Por favor, preencha o preço.")
            return
        
        try:
            price = float(price_str)
            if price <= 0:
                raise ValueError
        except ValueError:
            messagebox.showerror("Erro", "Por favor, insira um preço válido.")
            return
        
        db = get_db()
        conn = db.get_connection()
        cursor = conn.cursor()
        
        try:
            image_path_db = self.product_data.get('image_path')
            if self.image_path:
                products_dir = Path(__file__).parent.parent.parent / "assets" / "products"
                products_dir.mkdir(parents=True, exist_ok=True)
                
                import shutil
                file_ext = Path(self.image_path).suffix
                new_filename = f"{self.store_data['id']}_{name.replace(' ', '_')}{file_ext}"
                new_path = products_dir / new_filename
                shutil.copy2(self.image_path, new_path)
                image_path_db = str(new_path)
            
            cursor.execute("""
                UPDATE products 
                SET name = ?, description = ?, price = ?, image_path = ?
                WHERE id = ? AND store_id = ?
            """, (name, description if description else None, price, image_path_db, self.product_id, self.store_data['id']))
            
            conn.commit()
            messagebox.showinfo("Sucesso", "Produto atualizado com sucesso!")
            self.window.destroy()
            if self.products_page_ref:
                self.products_page_ref._load_products()
        
        except sqlite3.Error as e:
            messagebox.showerror("Erro", f"Erro ao atualizar produto: {str(e)}")
        except Exception as e:
            messagebox.showerror("Erro", f"Erro inesperado: {str(e)}")
    
    def _cancel(self):
        self.window.destroy()

