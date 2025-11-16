import sqlite3
import os
from pathlib import Path


class Database:
    
    def __init__(self, db_path: str = None):
        if db_path is None:
            # Caminho padrão: database/database.db
            base_dir = Path(__file__).parent.parent.parent
            db_path = base_dir / "database" / "database.db"
        
        self.db_path = db_path
        self.conn = None
        self._ensure_database_dir()
        self._initialize_database()
    
    def _ensure_database_dir(self):
        os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
    
    def _initialize_database(self):
        self.conn = sqlite3.connect(self.db_path)
        self.conn.row_factory = sqlite3.Row 
        self._create_tables()
        self._insert_default_admin()
    
    def _create_tables(self):
        cursor = self.conn.cursor()
        
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                email TEXT UNIQUE NOT NULL,
                password TEXT NOT NULL,
                user_type TEXT NOT NULL CHECK(user_type IN ('client', 'store', 'admin')),
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                is_active INTEGER DEFAULT 1,
                is_blocked INTEGER DEFAULT 0
            )
        """)
        
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS stores (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                name TEXT NOT NULL,
                description TEXT,
                image_path TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
            )
        """)
        
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS products (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                store_id INTEGER NOT NULL,
                name TEXT NOT NULL,
                description TEXT,
                price REAL NOT NULL,
                image_path TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                is_available INTEGER DEFAULT 1,
                FOREIGN KEY (store_id) REFERENCES stores(id) ON DELETE CASCADE
            )
        """)
        
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS orders (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                client_id INTEGER NOT NULL,
                store_id INTEGER NOT NULL,
                total_amount REAL NOT NULL,
                status TEXT NOT NULL DEFAULT 'Pendente' 
                    CHECK(status IN ('Pendente', 'Em preparo', 'Pronto', 'Entregue', 'Cancelado')),
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (client_id) REFERENCES users(id) ON DELETE CASCADE,
                FOREIGN KEY (store_id) REFERENCES stores(id) ON DELETE CASCADE
            )
        """)
        
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS order_items (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                order_id INTEGER NOT NULL,
                product_id INTEGER NOT NULL,
                quantity INTEGER NOT NULL DEFAULT 1,
                price REAL NOT NULL,
                FOREIGN KEY (order_id) REFERENCES orders(id) ON DELETE CASCADE,
                FOREIGN KEY (product_id) REFERENCES products(id) ON DELETE CASCADE
            )
        """)
        
        self.conn.commit()
    
    def _insert_default_admin(self):
        cursor = self.conn.cursor()
        
        cursor.execute("SELECT id FROM users WHERE user_type = 'admin' LIMIT 1")
        if cursor.fetchone() is None:
            cursor.execute("""
                INSERT INTO users (name, email, password, user_type)
                VALUES (?, ?, ?, ?)
            """, ("Administrador", "admin@urbanfood.com", "admin123", "admin"))
            self.conn.commit()
    
    def get_connection(self):
        if self.conn is None:
            self._initialize_database()
        return self.conn
    
    def close(self):
        if self.conn:
            self.conn.close()
            self.conn = None
    
    def __enter__(self):
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()


_db_instance = None


def get_db():
    global _db_instance
    if _db_instance is None:
        _db_instance = Database()
    return _db_instance


def init_database():
    db = get_db()
    return db

