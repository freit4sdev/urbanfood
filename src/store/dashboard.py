import tkinter as tk
from src.store.orders import StoreOrdersPage
from src.store.products import StoreProductsPage


class StoreDashboard:
    
    def __init__(self, parent, user_data, store_data):
        self.parent = parent
        self.user_data = user_data
        self.store_data = store_data
        self.window = tk.Toplevel(parent)
        self.window.title("UrbanFood - Loja")
        self.window.geometry("900x700")
        self.window.resizable(True, True)
        self.window.protocol("WM_DELETE_WINDOW", self._on_close)
        
        self.current_page = None
        self._create_widgets()
        self._show_orders()
    
    def _create_widgets(self):
        self.content_frame = tk.Frame(self.window)
        self.content_frame.pack(fill="both", expand=True)
        
        bottom_bar = tk.Frame(self.window, bg="#f0f0f0", height=60)
        bottom_bar.pack(side="bottom", fill="x")
        bottom_bar.pack_propagate(False)
        
        orders_btn = tk.Button(
            bottom_bar,
            text="📦 Pedidos",
            font=("Arial", 11),
            bg="#FF9800",
            fg="white",
            width=15,
            height=2,
            command=self._show_orders
        )
        orders_btn.pack(side="left", padx=10, pady=10)
        
        products_btn = tk.Button(
            bottom_bar,
            text="🍔 Produtos",
            font=("Arial", 11),
            bg="#757575",
            fg="white",
            width=15,
            height=2,
            command=self._show_products
        )
        products_btn.pack(side="left", padx=10, pady=10)
        
        logout_btn = tk.Button(
            bottom_bar,
            text="Sair",
            font=("Arial", 11),
            bg="#F44336",
            fg="white",
            width=10,
            height=2,
            command=self._on_close
        )
        logout_btn.pack(side="right", padx=10, pady=10)
        
        self.bottom_buttons = {
            "orders": orders_btn,
            "products": products_btn
        }
    
    def _clear_content(self):
        if self.current_page:
            try:
                if hasattr(self.current_page, 'window') and self.current_page.window.winfo_exists():
                    self.current_page.window.destroy()
            except:
                pass
        self.current_page = None
        for widget in self.content_frame.winfo_children():
            widget.destroy()
        self.window.update_idletasks()
    
    def _update_bottom_bar(self, active_button):
        colors = {
            "orders": "#FF9800",
            "products": "#FF9800"
        }
        inactive_color = "#757575"
        
        for key, btn in self.bottom_buttons.items():
            if key == active_button:
                btn.config(bg=colors[key])
            else:
                btn.config(bg=inactive_color)
    
    def _show_orders(self):
        self._clear_content()
        self._update_bottom_bar("orders")
        self.current_page = StoreOrdersPage(self.content_frame, self.user_data, self.store_data)
    
    def _show_products(self):
        self._clear_content()
        self._update_bottom_bar("products")
        self.current_page = StoreProductsPage(self.content_frame, self.user_data, self.store_data, self)
    
    def _on_close(self):
        self.window.destroy()
        if self.parent.winfo_exists():
            from src.auth.login import LoginWindow
            LoginWindow(self.parent)

