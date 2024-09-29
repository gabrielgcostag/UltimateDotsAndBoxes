import tkinter as tk
from tkinter import messagebox
from tkinter import ttk
from dots import DotGame

def show_menu():
    menu = tk.Tk()
    menu.title("Menu Principal")
    menu.geometry("300x200")
    menu.resizable(False, False)

    def start_game():
        menu.destroy()
        root = tk.Tk()
        game = DotGame(root, show_menu)
        root.mainloop()

    def show_settings():
        messagebox.showinfo("Configurações", "Aqui estarão as configurações. Como alterar cor, tamanho do tabuleiro, etc.")

    style = ttk.Style()
    style.configure('TButton', font=('Helvetica', 16), padding=10)
    style.configure('Start.TButton', background='green', foreground='black')
    style.configure('Settings.TButton', background='green', foreground='black')

    start_button = ttk.Button(menu, text="Começar Jogo", command=start_game, style='Start.TButton')
    start_button.pack(expand=True, pady=10)

    settings_button = ttk.Button(menu, text="Configurações", command=show_settings, style='Settings.TButton')
    settings_button.pack(expand=True, pady=10)

    menu.mainloop()