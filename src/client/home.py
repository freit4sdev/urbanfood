import tkinter as tk
from tkinter import ttk, messagebox
import sqlite3
from src.services.database import get_db
from src.services.cart_service import CartService


class HomePage:
    
    def __init__(self, parent, user_data, dashboard_ref=None):
        self.parent = parent
        self.user_data = user_data
        self.dashboard_ref = dashboard_ref
        self.window = parent
        self.cart_service = CartService()
        
        self._create_widgets()
        self._load_stores_and_products()
    
    def _create_widgets(self):
        header_frame = tk.Frame(self.window, bg="#2196F3", height=80)
        header_frame.pack(fill="x")
        header_frame.pack_propagate(False)
        
        title_label = tk.Label(
            header_frame,
            text="🍔 UrbanFood",
            font=("Arial", 24, "bold"),
            bg="#2196F3",
            fg="white"
        )
        title_label.pack(pady=15)
        
        welcome_label = tk.Label(
            header_frame,
            text=f"Bem-vindo, {self.user_data.get('name', 'Cliente')}!",
            font=("Arial", 12),
            bg="#2196F3",
            fg="white"
        )
        welcome_label.pack()
        
        search_frame = tk.Frame(self.window)
        search_frame.pack(fill="x", padx=20, pady=10)
        
        search_label = tk.Label(search_frame, text="🔍 Buscar lojas:", font=("Arial", 10))
        search_label.pack(side="left", padx=5)
        
        self.search_entry = tk.Entry(search_frame, font=("Arial", 11), width=30)
        self.search_entry.pack(side="left", padx=5)
        self.search_entry.bind("<KeyRelease>", self._on_search)
        
        clear_btn = tk.Button(
            search_frame,
            text="Limpar",
            font=("Arial", 10),
            command=self._clear_search
        )
        clear_btn.pack(side="left", padx=5)
        
        main_frame = tk.Frame(self.window)
        main_frame.pack(fill="both", expand=True, padx=20, pady=10)
        
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
    
    def _load_stores_and_products(self):
        for widget in self.products_frame.winfo_children():
            widget.destroy()
        
        db = get_db()
        conn = db.get_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute("""
                SELECT s.id as store_id, s.name as store_name, s.description as store_description,
                       p.id as product_id, p.name as product_name, p.description as product_description,
                       p.price, p.image_path as product_image
                FROM stores s
                LEFT JOIN products p ON s.id = p.store_id AND p.is_available = 1
                ORDER BY s.name, p.name
            """)
            
            results = cursor.fetchall()
            
            current_store = None
            store_frame = None
            
            for row in results:
                if current_store != row['store_id']:
                    if store_frame:
                        tk.Label(store_frame, text="", bg="white", height=1).pack()
                    
                    current_store = row['store_id']
                    
                    store_frame = tk.Frame(self.products_frame, bg="white", relief="solid", bd=1)
                    store_frame.pack(fill="x", padx=10, pady=10)
                    
                    store_header = tk.Frame(store_frame, bg="#FF9800", height=50)
                    store_header.pack(fill="x")
                    store_header.pack_propagate(False)
                    
                    store_name_label = tk.Label(
                        store_header,
                        text=f"🏪 {row['store_name']}",
                        font=("Arial", 16, "bold"),
                        bg="#FF9800",
                        fg="white"
                    )
                    store_name_label.pack(pady=10)
                    
                    if row['store_description']:
                        store_desc_label = tk.Label(
                            store_frame,
                            text=row['store_description'],
                            font=("Arial", 10),
                            bg="white",
                            wraplength=800,
                            justify="left"
                        )
                        store_desc_label.pack(pady=5, padx=10, anchor="w")
                    
                    products_container = tk.Frame(store_frame, bg="white")
                    products_container.pack(fill="x", padx=10, pady=10)
                
                if row['product_id']:
                    product_frame = tk.Frame(products_container, bg="#f5f5f5", relief="solid", bd=1)
                    product_frame.pack(fill="x", pady=5, padx=5)
                    
                    product_info = tk.Frame(product_frame, bg="#f5f5f5")
                    product_info.pack(fill="x", padx=10, pady=10)
                    
                    product_name_label = tk.Label(
                        product_info,
                        text=row['product_name'],
                        font=("Arial", 12, "bold"),
                        bg="#f5f5f5",
                        anchor="w"
                    )
                    product_name_label.pack(fill="x")
                    
                    if row['product_description']:
                        product_desc_label = tk.Label(
                            product_info,
                            text=row['product_description'],
                            font=("Arial", 9),
                            bg="#f5f5f5",
                            anchor="w",
                            wraplength=600
                        )
                        product_desc_label.pack(fill="x", pady=2)
                    
                    price_frame = tk.Frame(product_info, bg="#f5f5f5")
                    price_frame.pack(fill="x", pady=5)
                    
                    price_label = tk.Label(
                        price_frame,
                        text=f"R$ {row['price']:.2f}",
                        font=("Arial", 14, "bold"),
                        bg="#f5f5f5",
                        fg="#4CAF50"
                    )
                    price_label.pack(side="left")
                    
                    add_btn = tk.Button(
                        price_frame,
                        text="➕ Adicionar",
                        font=("Arial", 10),
                        bg="#4CAF50",
                        fg="white",
                        command=lambda pid=row['product_id'], pname=row['product_name'], pprice=row['price'], sid=row['store_id'], sname=row['store_name']: self._add_to_cart(pid, pname, pprice, sid, sname)
                    )
                    add_btn.pack(side="right", padx=5)
            
            if not results:
                no_data_label = tk.Label(
                    self.products_frame,
                    text="Nenhuma loja ou produto encontrado.",
                    font=("Arial", 14),
                    bg="white"
                )
                no_data_label.pack(pady=50)
        
        except sqlite3.Error as e:
            messagebox.showerror("Erro", f"Erro ao carregar dados: {str(e)}")
    
    def _on_search(self, event=None):
        search_term = self.search_entry.get().strip().lower()
        
        if not search_term:
            self._load_stores_and_products()
            return
        
        for widget in self.products_frame.winfo_children():
            widget.destroy()
        
        db = get_db()
        conn = db.get_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute("""
                SELECT s.id as store_id, s.name as store_name, s.description as store_description,
                       p.id as product_id, p.name as product_name, p.description as product_description,
                       p.price, p.image_path as product_image
                FROM stores s
                LEFT JOIN products p ON s.id = p.store_id AND p.is_available = 1
                WHERE s.name LIKE ? OR p.name LIKE ?
                ORDER BY s.name, p.name
            """, (f"%{search_term}%", f"%{search_term}%"))
            
            results = cursor.fetchall()
            
            current_store = None
            store_frame = None
            
            for row in results:
                if current_store != row['store_id']:
                    if store_frame:
                        tk.Label(store_frame, text="", bg="white", height=1).pack()
                    
                    current_store = row['store_id']
                    
                    store_frame = tk.Frame(self.products_frame, bg="white", relief="solid", bd=1)
                    store_frame.pack(fill="x", padx=10, pady=10)
                    
                    store_header = tk.Frame(store_frame, bg="#FF9800", height=50)
                    store_header.pack(fill="x")
                    store_header.pack_propagate(False)
                    
                    store_name_label = tk.Label(
                        store_header,
                        text=f"🏪 {row['store_name']}",
                        font=("Arial", 16, "bold"),
                        bg="#FF9800",
                        fg="white"
                    )
                    store_name_label.pack(pady=10)
                    
                    if row['store_description']:
                        store_desc_label = tk.Label(
                            store_frame,
                            text=row['store_description'],
                            font=("Arial", 10),
                            bg="white",
                            wraplength=800,
                            justify="left"
                        )
                        store_desc_label.pack(pady=5, padx=10, anchor="w")
                    
                    products_container = tk.Frame(store_frame, bg="white")
                    products_container.pack(fill="x", padx=10, pady=10)
                
                if row['product_id']:
                    product_frame = tk.Frame(products_container, bg="#f5f5f5", relief="solid", bd=1)
                    product_frame.pack(fill="x", pady=5, padx=5)
                    
                    product_info = tk.Frame(product_frame, bg="#f5f5f5")
                    product_info.pack(fill="x", padx=10, pady=10)
                    
                    product_name_label = tk.Label(
                        product_info,
                        text=row['product_name'],
                        font=("Arial", 12, "bold"),
                        bg="#f5f5f5",
                        anchor="w"
                    )
                    product_name_label.pack(fill="x")
                    
                    if row['product_description']:
                        product_desc_label = tk.Label(
                            product_info,
                            text=row['product_description'],
                            font=("Arial", 9),
                            bg="#f5f5f5",
                            anchor="w",
                            wraplength=600
                        )
                        product_desc_label.pack(fill="x", pady=2)
                    
                    price_frame = tk.Frame(product_info, bg="#f5f5f5")
                    price_frame.pack(fill="x", pady=5)
                    
                    price_label = tk.Label(
                        price_frame,
                        text=f"R$ {row['price']:.2f}",
                        font=("Arial", 14, "bold"),
                        bg="#f5f5f5",
                        fg="#4CAF50"
                    )
                    price_label.pack(side="left")
                    
                    add_btn = tk.Button(
                        price_frame,
                        text="➕ Adicionar",
                        font=("Arial", 10),
                        bg="#4CAF50",
                        fg="white",
                        command=lambda pid=row['product_id'], pname=row['product_name'], pprice=row['price'], sid=row['store_id'], sname=row['store_name']: self._add_to_cart(pid, pname, pprice, sid, sname)
                    )
                    add_btn.pack(side="right", padx=5)
            
            if not results:
                no_data_label = tk.Label(
                    self.products_frame,
                    text="Nenhum resultado encontrado.",
                    font=("Arial", 14),
                    bg="white"
                )
                no_data_label.pack(pady=50)
        
        except sqlite3.Error as e:
            messagebox.showerror("Erro", f"Erro ao buscar: {str(e)}")
    
    def _clear_search(self):
        self.search_entry.delete(0, tk.END)
        self._load_stores_and_products()
    
    def _add_to_cart(self, product_id, product_name, price, store_id, store_name):
        self.cart_service.add_item(product_id, product_name, price, store_id, store_name)
        messagebox.showinfo("Sucesso", f"'{product_name}' adicionado ao carrinho!")

