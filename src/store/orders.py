import tkinter as tk
from tkinter import ttk, messagebox
import sqlite3
from src.services.database import get_db
from datetime import datetime


class StoreOrdersPage:
    
    def __init__(self, parent, user_data, store_data):
        self.parent = parent
        self.user_data = user_data
        self.store_data = store_data
        
        self._create_widgets()
        self._load_orders()
    
    def _create_widgets(self):
        header_frame = tk.Frame(self.parent, bg="#FF9800", height=80)
        header_frame.pack(fill="x")
        header_frame.pack_propagate(False)
        
        title_label = tk.Label(
            header_frame,
            text="📦 Pedidos Recebidos",
            font=("Arial", 24, "bold"),
            bg="#FF9800",
            fg="white"
        )
        title_label.pack(pady=25)
        
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
        
        self.orders_frame = scrollable_frame
    
    def _load_orders(self):
        for widget in self.orders_frame.winfo_children():
            widget.destroy()
        
        db = get_db()
        conn = db.get_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute("""
                SELECT o.id, o.total_amount, o.status, o.created_at, o.updated_at,
                       u.name as client_name, u.id as client_id
                FROM orders o
                INNER JOIN users u ON o.client_id = u.id
                WHERE o.store_id = ?
                ORDER BY o.created_at DESC
            """, (self.store_data['id'],))
            
            orders = cursor.fetchall()
            
            if not orders:
                no_orders_label = tk.Label(
                    self.orders_frame,
                    text="Nenhum pedido recebido ainda.",
                    font=("Arial", 14),
                    bg="white",
                    fg="#757575"
                )
                no_orders_label.pack(pady=50)
                return
            
            for order in orders:
                order_frame = tk.Frame(self.orders_frame, bg="white", relief="solid", bd=2)
                order_frame.pack(fill="x", padx=10, pady=10)
                
                header_order = tk.Frame(order_frame, bg="#2196F3", height=50)
                header_order.pack(fill="x")
                header_order.pack_propagate(False)
                
                order_info_top = tk.Frame(header_order, bg="#2196F3")
                order_info_top.pack(fill="x", padx=15, pady=5)
                
                client_label = tk.Label(
                    order_info_top,
                    text=f"👤 Cliente: {order['client_name']}",
                    font=("Arial", 16, "bold"),
                    bg="#2196F3",
                    fg="white"
                )
                client_label.pack(side="left")
                
                status_color = self._get_status_color(order['status'])
                status_label = tk.Label(
                    order_info_top,
                    text=order['status'],
                    font=("Arial", 12, "bold"),
                    bg=status_color,
                    fg="white",
                    padx=10,
                    pady=5
                )
                status_label.pack(side="right", padx=5)
                
                order_id_label = tk.Label(
                    header_order,
                    text=f"Pedido #{order['id']}",
                    font=("Arial", 10),
                    bg="#2196F3",
                    fg="white"
                )
                order_id_label.pack(pady=2)
                
                content_order = tk.Frame(order_frame, bg="white")
                content_order.pack(fill="x", padx=15, pady=10)
                
                cursor.execute("""
                    SELECT oi.quantity, oi.price, p.name as product_name
                    FROM order_items oi
                    INNER JOIN products p ON oi.product_id = p.id
                    WHERE oi.order_id = ?
                """, (order['id'],))
                
                items = cursor.fetchall()
                
                items_label = tk.Label(
                    content_order,
                    text="Itens:",
                    font=("Arial", 12, "bold"),
                    bg="white",
                    anchor="w"
                )
                items_label.pack(fill="x", pady=(0, 5))
                
                for item in items:
                    item_text = f"  • {item['product_name']} x{item['quantity']} = R$ {item['price'] * item['quantity']:.2f}"
                    item_label = tk.Label(
                        content_order,
                        text=item_text,
                        font=("Arial", 10),
                        bg="white",
                        anchor="w",
                        fg="#424242"
                    )
                    item_label.pack(fill="x", padx=10)
                
                separator = tk.Frame(content_order, bg="#e0e0e0", height=1)
                separator.pack(fill="x", pady=10)
                
                bottom_info = tk.Frame(content_order, bg="white")
                bottom_info.pack(fill="x")
                
                date_str = self._format_date(order['created_at'])
                date_label = tk.Label(
                    bottom_info,
                    text=f"📅 {date_str}",
                    font=("Arial", 10),
                    bg="white",
                    fg="#757575"
                )
                date_label.pack(side="left")
                
                total_label = tk.Label(
                    bottom_info,
                    text=f"Total: R$ {order['total_amount']:.2f}",
                    font=("Arial", 14, "bold"),
                    bg="white",
                    fg="#4CAF50"
                )
                total_label.pack(side="right")
                
                status_frame = tk.Frame(content_order, bg="white")
                status_frame.pack(fill="x", pady=10)
                
                status_label_text = tk.Label(
                    status_frame,
                    text="Atualizar status:",
                    font=("Arial", 10, "bold"),
                    bg="white"
                )
                status_label_text.pack(side="left", padx=5)
                
                status_options = ['Pendente', 'Em preparo', 'Pronto', 'Entregue', 'Cancelado']
                current_status = order['status']
                
                for status in status_options:
                    if status != current_status:
                        status_btn = tk.Button(
                            status_frame,
                            text=status,
                            font=("Arial", 9),
                            bg="#757575",
                            fg="white",
                            command=lambda s=status, oid=order['id']: self._update_status(oid, s)
                        )
                        status_btn.pack(side="left", padx=2)
        
        except sqlite3.Error as e:
            messagebox.showerror("Erro", f"Erro ao carregar pedidos: {str(e)}")
    
    def _update_status(self, order_id, new_status):
        db = get_db()
        conn = db.get_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute("""
                UPDATE orders 
                SET status = ?, updated_at = CURRENT_TIMESTAMP
                WHERE id = ? AND store_id = ?
            """, (new_status, order_id, self.store_data['id']))
            
            conn.commit()
            messagebox.showinfo("Sucesso", f"Status do pedido atualizado para: {new_status}")
            self._load_orders()
        
        except sqlite3.Error as e:
            messagebox.showerror("Erro", f"Erro ao atualizar status: {str(e)}")
    
    def _get_status_color(self, status):
        colors = {
            'Pendente': '#FFC107',
            'Em preparo': '#2196F3',
            'Pronto': '#9C27B0',
            'Entregue': '#4CAF50',
            'Cancelado': '#F44336'
        }
        return colors.get(status, '#757575')
    
    def _format_date(self, date_str):
        try:
            if isinstance(date_str, str):
                dt = datetime.strptime(date_str, '%Y-%m-%d %H:%M:%S')
            else:
                dt = datetime.fromisoformat(date_str.replace('Z', '+00:00'))
            
            return dt.strftime('%d/%m/%Y às %H:%M')
        except:
            return date_str

