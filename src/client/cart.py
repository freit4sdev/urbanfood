import tkinter as tk
from tkinter import messagebox
from src.services.cart_service import CartService
from src.client.payment import PaymentWindow


class CartPage:
    
    def __init__(self, parent, user_data, dashboard_ref=None):
        self.parent = parent
        self.user_data = user_data
        self.dashboard_ref = dashboard_ref
        self.cart_service = CartService()
        
        self._create_widgets()
        self._load_cart()
    
    def _create_widgets(self):
        header_frame = tk.Frame(self.parent, bg="#4CAF50", height=80)
        header_frame.pack(fill="x")
        header_frame.pack_propagate(False)
        
        title_label = tk.Label(
            header_frame,
            text="🛒 Carrinho de Compras",
            font=("Arial", 24, "bold"),
            bg="#4CAF50",
            fg="white"
        )
        title_label.pack(pady=25)
        
        main_frame = tk.Frame(self.parent)
        main_frame.pack(fill="both", expand=True, padx=20, pady=20)
        
        canvas = tk.Canvas(main_frame, bg="white")
        scrollbar = tk.Scrollbar(main_frame, orient="vertical", command=canvas.yview)
        scrollable_frame = tk.Frame(canvas, bg="white")
        
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        self.items_frame = scrollable_frame
        
        summary_frame = tk.Frame(self.parent, bg="#f5f5f5", height=100)
        summary_frame.pack(fill="x", side="bottom")
        summary_frame.pack_propagate(False)
        
        total_label = tk.Label(
            summary_frame,
            text="Total: R$ 0,00",
            font=("Arial", 18, "bold"),
            bg="#f5f5f5"
        )
        total_label.pack(pady=10)
        self.total_label = total_label
        
        button_frame = tk.Frame(summary_frame, bg="#f5f5f5")
        button_frame.pack(pady=10)
        
        clear_btn = tk.Button(
            button_frame,
            text="Limpar Carrinho",
            font=("Arial", 11),
            bg="#F44336",
            fg="white",
            command=self._clear_cart
        )
        clear_btn.pack(side="left", padx=5)
        
        checkout_btn = tk.Button(
            button_frame,
            text="Finalizar Pedido",
            font=("Arial", 11, "bold"),
            bg="#4CAF50",
            fg="white",
            command=self._checkout
        )
        checkout_btn.pack(side="left", padx=5)
    
    def _load_cart(self):
        for widget in self.items_frame.winfo_children():
            widget.destroy()
        
        cart = self.cart_service.get_cart()
        
        if not cart:
            empty_label = tk.Label(
                self.items_frame,
                text="Seu carrinho está vazio.",
                font=("Arial", 14),
                bg="white",
                fg="#757575"
            )
            empty_label.pack(pady=50)
            self.total_label.config(text="Total: R$ 0,00")
            return
        
        stores = self.cart_service.get_stores_in_cart()
        
        for store_id, store_data in stores.items():
            store_frame = tk.Frame(self.items_frame, bg="white", relief="solid", bd=1)
            store_frame.pack(fill="x", padx=10, pady=10)
            
            store_header = tk.Frame(store_frame, bg="#FF9800", height=40)
            store_header.pack(fill="x")
            store_header.pack_propagate(False)
            
            store_name_label = tk.Label(
                store_header,
                text=f"🏪 {store_data['store_name']}",
                font=("Arial", 14, "bold"),
                bg="#FF9800",
                fg="white"
            )
            store_name_label.pack(pady=8)
            
            for item in store_data['items']:
                item_frame = tk.Frame(store_frame, bg="#f5f5f5", relief="solid", bd=1)
                item_frame.pack(fill="x", padx=5, pady=5)
                
                item_info = tk.Frame(item_frame, bg="#f5f5f5")
                item_info.pack(fill="x", padx=10, pady=10)
                
                name_label = tk.Label(
                    item_info,
                    text=item['product_name'],
                    font=("Arial", 12, "bold"),
                    bg="#f5f5f5",
                    anchor="w"
                )
                name_label.pack(fill="x")
                
                controls_frame = tk.Frame(item_info, bg="#f5f5f5")
                controls_frame.pack(fill="x", pady=5)
                
                quantity_frame = tk.Frame(controls_frame, bg="#f5f5f5")
                quantity_frame.pack(side="left")
                
                qty_label = tk.Label(
                    quantity_frame,
                    text="Quantidade:",
                    font=("Arial", 10),
                    bg="#f5f5f5"
                )
                qty_label.pack(side="left", padx=5)
                
                minus_btn = tk.Button(
                    quantity_frame,
                    text="-",
                    font=("Arial", 10, "bold"),
                    width=3,
                    command=lambda pid=item['product_id'], qty=item['quantity']-1: self._update_quantity(pid, qty)
                )
                minus_btn.pack(side="left", padx=2)
                
                qty_value = tk.Label(
                    quantity_frame,
                    text=str(item['quantity']),
                    font=("Arial", 12, "bold"),
                    bg="#f5f5f5",
                    width=3
                )
                qty_value.pack(side="left", padx=2)
                
                plus_btn = tk.Button(
                    quantity_frame,
                    text="+",
                    font=("Arial", 10, "bold"),
                    width=3,
                    command=lambda pid=item['product_id'], qty=item['quantity']+1: self._update_quantity(pid, qty)
                )
                plus_btn.pack(side="left", padx=2)
                
                price_frame = tk.Frame(controls_frame, bg="#f5f5f5")
                price_frame.pack(side="right")
                
                item_total = item['price'] * item['quantity']
                price_label = tk.Label(
                    price_frame,
                    text=f"R$ {item_total:.2f}",
                    font=("Arial", 14, "bold"),
                    bg="#f5f5f5",
                    fg="#4CAF50"
                )
                price_label.pack(side="left", padx=10)
                
                remove_btn = tk.Button(
                    price_frame,
                    text="🗑️",
                    font=("Arial", 10),
                    bg="#F44336",
                    fg="white",
                    command=lambda pid=item['product_id']: self._remove_item(pid)
                )
                remove_btn.pack(side="left", padx=5)
        
        total = self.cart_service.get_total()
        self.total_label.config(text=f"Total: R$ {total:.2f}")
    
    def _update_quantity(self, product_id, quantity):
        self.cart_service.update_quantity(product_id, quantity)
        self._load_cart()
    
    def _remove_item(self, product_id):
        self.cart_service.remove_item(product_id)
        self._load_cart()
    
    def _clear_cart(self):
        if messagebox.askyesno("Confirmar", "Deseja limpar todo o carrinho?"):
            self.cart_service.clear()
            self._load_cart()
    
    def _checkout(self):
        cart = self.cart_service.get_cart()
        if not cart:
            messagebox.showwarning("Aviso", "Seu carrinho está vazio.")
            return
        
        stores = self.cart_service.get_stores_in_cart()
        if len(stores) > 1:
            messagebox.showwarning("Aviso", "Por favor, finalize pedidos de uma loja por vez.")
            return
        
        store_id = list(stores.keys())[0]
        if self.dashboard_ref:
            PaymentWindow(self.dashboard_ref.window, self.user_data, store_id, self.cart_service, self.dashboard_ref)
        else:
            PaymentWindow(self.parent.winfo_toplevel(), self.user_data, store_id, self.cart_service, self.dashboard_ref)


