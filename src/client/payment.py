import tkinter as tk
from tkinter import messagebox
import sqlite3
from src.services.database import get_db
from src.services.cart_service import CartService
from pathlib import Path


class PaymentWindow:
    
    def __init__(self, parent, user_data, store_id, cart_service, dashboard_ref=None):
        self.parent = parent
        self.user_data = user_data
        self.store_id = store_id
        self.cart_service = cart_service
        self.dashboard_ref = dashboard_ref
        
        self.window = tk.Toplevel(parent)
        self.window.title("Pagamento")
        self.window.geometry("600x700")
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
        header_frame = tk.Frame(self.window, bg="#9C27B0", height=60)
        header_frame.pack(fill="x")
        header_frame.pack_propagate(False)
        
        title_label = tk.Label(
            header_frame,
            text="💳 Pagamento",
            font=("Arial", 20, "bold"),
            bg="#9C27B0",
            fg="white"
        )
        title_label.pack(pady=15)
        
        content_frame = tk.Frame(self.window)
        content_frame.pack(fill="both", expand=True, padx=20, pady=20)
        
        summary_label = tk.Label(
            content_frame,
            text="Resumo do Pedido",
            font=("Arial", 16, "bold")
        )
        summary_label.pack(pady=10)
        
        canvas = tk.Canvas(content_frame, bg="white", height=200)
        scrollbar = tk.Scrollbar(content_frame, orient="vertical", command=canvas.yview)
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
        self._load_order_summary()
        
        total_frame = tk.Frame(content_frame, bg="#f5f5f5", height=50)
        total_frame.pack(fill="x", pady=10)
        total_frame.pack_propagate(False)
        
        total = self.cart_service.get_total()
        total_label = tk.Label(
            total_frame,
            text=f"Total: R$ {total:.2f}",
            font=("Arial", 18, "bold"),
            bg="#f5f5f5"
        )
        total_label.pack(pady=10)
        
        payment_label = tk.Label(
            content_frame,
            text="Escaneie o QR Code para pagar via PIX",
            font=("Arial", 12, "bold")
        )
        payment_label.pack(pady=10)
        
        qr_frame = tk.Frame(content_frame, bg="white", relief="solid", bd=2)
        qr_frame.pack(pady=10)
        
        qr_path = Path(__file__).parent.parent.parent / "assets" / "qrcode_pix.png"
        
        if qr_path.exists():
            try:
                from PIL import Image, ImageTk
                img = Image.open(qr_path)
                img = img.resize((200, 200), Image.Resampling.LANCZOS)
                photo = ImageTk.PhotoImage(img)
                qr_label = tk.Label(qr_frame, image=photo, bg="white")
                qr_label.image = photo
                qr_label.pack(padx=20, pady=20)
            except Exception as e:
                print(f"Erro ao carregar imagem do QR Code: {e}")
                qr_placeholder = tk.Label(
                    qr_frame,
                    text="QR Code PIX\n(Imagem não encontrada)",
                    font=("Arial", 12),
                    bg="white",
                    width=25,
                    height=10
                )
                qr_placeholder.pack(padx=20, pady=20)
        else:
            qr_placeholder = tk.Label(
                qr_frame,
                text="QR Code PIX\n(Imagem não encontrada)\n\nColoque o arquivo qrcode_pix.png\nna pasta assets/",
                font=("Arial", 10),
                bg="white",
                width=30,
                height=10,
                justify="center"
            )
            qr_placeholder.pack(padx=20, pady=20)
        
        button_frame = tk.Frame(content_frame)
        button_frame.pack(pady=20)
        
        confirm_btn = tk.Button(
            button_frame,
            text="Confirmar Pagamento",
            font=("Arial", 12, "bold"),
            bg="#4CAF50",
            fg="white",
            width=20,
            height=2,
            command=self._confirm_payment
        )
        confirm_btn.pack(side="left", padx=5)
        
        cancel_btn = tk.Button(
            button_frame,
            text="Cancelar",
            font=("Arial", 12),
            width=15,
            height=2,
            command=self._cancel
        )
        cancel_btn.pack(side="left", padx=5)
    
    def _load_order_summary(self):
        for widget in self.items_frame.winfo_children():
            widget.destroy()
        
        stores = self.cart_service.get_stores_in_cart()
        store_data = stores[self.store_id]
        
        store_label = tk.Label(
            self.items_frame,
            text=f"Loja: {store_data['store_name']}",
            font=("Arial", 14, "bold"),
            bg="white"
        )
        store_label.pack(pady=5, anchor="w")
        
        for item in store_data['items']:
            item_frame = tk.Frame(self.items_frame, bg="white")
            item_frame.pack(fill="x", pady=2, padx=10)
            
            item_text = f"{item['product_name']} x{item['quantity']} = R$ {item['price'] * item['quantity']:.2f}"
            item_label = tk.Label(
                item_frame,
                text=item_text,
                font=("Arial", 11),
                bg="white",
                anchor="w"
            )
            item_label.pack(fill="x")
    
    def _confirm_payment(self):
        cart = self.cart_service.get_cart()
        if not cart:
            messagebox.showwarning("Aviso", "Carrinho vazio.")
            return
        
        db = get_db()
        conn = db.get_connection()
        cursor = conn.cursor()
        
        try:
            total = self.cart_service.get_total()
            
            cursor.execute(
                "INSERT INTO orders (client_id, store_id, total_amount, status) VALUES (?, ?, ?, ?)",
                (self.user_data['id'], self.store_id, total, 'Pendente')
            )
            order_id = cursor.lastrowid
            
            for item in cart.values():
                cursor.execute(
                    "INSERT INTO order_items (order_id, product_id, quantity, price) VALUES (?, ?, ?, ?)",
                    (order_id, item['product_id'], item['quantity'], item['price'])
                )
            
            conn.commit()
            
            self.cart_service.clear()
            messagebox.showinfo("Sucesso", "Pedido confirmado com sucesso!")
            self.window.destroy()
            
            if self.dashboard_ref:
                self.dashboard_ref._show_orders()
        
        except sqlite3.Error as e:
            messagebox.showerror("Erro", f"Erro ao confirmar pedido: {str(e)}")
    
    def _cancel(self):
        self.window.destroy()


