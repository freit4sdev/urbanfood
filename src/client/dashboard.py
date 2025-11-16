import tkinter as tk
from src.client.home import HomePage
from src.client.orders import OrdersPage
from src.client.stores import StoresPage
from src.client.cart import CartPage


class ClientDashboard:
    
    def __init__(self, parent, user_data):
        self.parent = parent
        self.user_data = user_data
        self.window = tk.Toplevel(parent)
        self.window.title("UrbanFood - Cliente")
        self.window.geometry("900x700")
        self.window.resizable(True, True)
        self.window.protocol("WM_DELETE_WINDOW", self._on_close)
        
        self.current_page = None
        self._create_widgets()
        self._show_home()
    
    def _create_widgets(self):
        self.content_frame = tk.Frame(self.window)
        self.content_frame.pack(fill="both", expand=True)
        
        bottom_bar = tk.Frame(self.window, bg="#f0f0f0", height=60)
        bottom_bar.pack(side="bottom", fill="x")
        bottom_bar.pack_propagate(False)
        
        home_btn = tk.Button(
            bottom_bar,
            text="🏠 Início",
            font=("Arial", 11),
            bg="#2196F3",
            fg="white",
            width=15,
            height=2,
            command=self._show_home
        )
        home_btn.pack(side="left", padx=10, pady=10)
        
        orders_btn = tk.Button(
            bottom_bar,
            text="📦 Pedidos",
            font=("Arial", 11),
            bg="#757575",
            fg="white",
            width=15,
            height=2,
            command=self._show_orders
        )
        orders_btn.pack(side="left", padx=10, pady=10)
        
        stores_btn = tk.Button(
            bottom_bar,
            text="🏪 Lojas",
            font=("Arial", 11),
            bg="#757575",
            fg="white",
            width=15,
            height=2,
            command=self._show_stores
        )
        stores_btn.pack(side="left", padx=10, pady=10)
        
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
        
        cart_btn = tk.Button(
            bottom_bar,
            text="🛒 Carrinho",
            font=("Arial", 11),
            bg="#757575",
            fg="white",
            width=15,
            height=2,
            command=self._show_cart
        )
        cart_btn.pack(side="left", padx=10, pady=10)
        
        self.bottom_buttons = {
            "home": home_btn,
            "orders": orders_btn,
            "stores": stores_btn,
            "cart": cart_btn
        }
    
    def _clear_content(self):
        for widget in self.content_frame.winfo_children():
            widget.destroy()
        if self.current_page:
            try:
                if hasattr(self.current_page, 'window') and self.current_page.window.winfo_exists():
                    self.current_page.window.destroy()
            except:
                pass
    
    def _update_bottom_bar(self, active_button):
        colors = {
            "home": "#2196F3",
            "orders": "#2196F3",
            "stores": "#2196F3",
            "cart": "#4CAF50"
        }
        inactive_color = "#757575"
        
        for key, btn in self.bottom_buttons.items():
            if key == active_button:
                btn.config(bg=colors[key])
            else:
                btn.config(bg=inactive_color)
    
    def _show_home(self):
        self._clear_content()
        self._update_bottom_bar("home")
        self.current_page = HomePage(self.content_frame, self.user_data, self)
    
    def _show_orders(self):
        self._clear_content()
        self._update_bottom_bar("orders")
        self.current_page = OrdersPage(self.content_frame, self.user_data)
    
    def _show_stores(self):
        self._clear_content()
        self._update_bottom_bar("stores")
        self.current_page = StoresPage(self.content_frame, self.user_data)
    
    def _show_cart(self):
        self._clear_content()
        self._update_bottom_bar("cart")
        self.current_page = CartPage(self.content_frame, self.user_data, self)
    
    def _on_close(self):
        self.window.destroy()
        if self.parent.winfo_exists():
            from src.auth.login import LoginWindow
            LoginWindow(self.parent)

