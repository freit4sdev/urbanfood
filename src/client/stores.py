import tkinter as tk
from tkinter import messagebox


class StoresPage:
    
    def __init__(self, parent, user_data):
        self.parent = parent
        self.user_data = user_data
        self.window = parent
        
        self._create_widgets()
    
    def _create_widgets(self):
        header_frame = tk.Frame(self.window, bg="#2196F3", height=80)
        header_frame.pack(fill="x")
        header_frame.pack_propagate(False)
        
        title_label = tk.Label(
            header_frame,
            text="🏪 Lojas",
            font=("Arial", 24, "bold"),
            bg="#2196F3",
            fg="white"
        )
        title_label.pack(pady=25)
        
        content_frame = tk.Frame(self.window)
        content_frame.pack(fill="both", expand=True, padx=20, pady=20)
        
        info_label = tk.Label(
            content_frame,
            text="Lista de lojas aparecerá aqui.",
            font=("Arial", 14),
            fg="#757575"
        )
        info_label.pack(pady=50)


