import tkinter as tk
from src.services.database import init_database
from src.auth.login import LoginWindow


def main():
    print("Inicializando banco de dados...")
    init_database()
    print("Banco de dados inicializado com sucesso!")
    
    
    root = tk.Tk()
    root.withdraw()
    
    login_window = LoginWindow(root)
    
    root.mainloop()


if __name__ == "__main__":
    main()

