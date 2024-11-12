import tkinter as tk
from tkinter import messagebox
from tkinter import ttk
from tabuleiro import Tabuleiro
from PIL import Image as ImagePil
from PIL import ImageTk

class PlayerInterface:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Menu Principal")
        self.root.geometry("300x200")
        self.root.resizable(False, False)
        self.board = Tabuleiro()
        self.create_menu()
        self.enough_players = False
        self.start = False
        self.rec_start = False
        self.rec_withdrawal = False
        self.rec_move = False
        self.reset = False

    def create_menu(self):
        menubar = tk.Menu(self.root)
        self.root.config(menu=menubar)

        style = ttk.Style()
        style.configure('TButton', font=('Helvetica', 16), padding=10)
        style.configure('Start.TButton', background='green', foreground='black')
        style.configure('Settings.TButton', background='green', foreground='black')

        start_button = ttk.Button(self.root, text="Começar Jogo", command=self.start_game, style='Start.TButton')
        start_button.pack(expand=True, pady=10)

        settings_button = ttk.Button(self.root, text="Configurações", command=self.show_settings, style='Settings.TButton')
        settings_button.pack(expand=True, pady=10)

    def start_game(self):
        self.root.destroy()
        game_root = tk.Tk()
        game_root.title("Jogo")
        game_root.geometry("620x650")
        game_root.resizable(False, False)

        top_frame = tk.Frame(game_root)
        top_frame.pack(side=tk.TOP, fill=tk.X, pady=5)

        back_button = ttk.Button(top_frame, text="← Menu", command=lambda: self.back_to_menu(game_root), width=10)
        back_button.pack(side=tk.LEFT, padx=5)

        game_frame = tk.Frame(game_root)
        game_frame.pack()

        canvas = tk.Canvas(game_frame, width=620, height=620, bg='white')
        canvas.pack()

        # background_image = ImagePil.open("aplication/assets/wood_background.jpg")
        # background_image = background_image.resize((620, 620))
        # background_photo = ImageTk.PhotoImage(background_image)
        # canvas.create_image(0, 0, image=background_photo, anchor=tk.NW)

        self.board = Tabuleiro()
        self.board.create_board(canvas)

        canvas.bind("<ButtonPress-1>", self.board.on_press)
        canvas.bind("<B1-Motion>", self.board.on_drag)
        canvas.bind("<ButtonRelease-1>", self.board.on_release)

        game_root.mainloop()

    def back_to_menu(self, game_root):
        game_root.destroy()
        self.__init__()

    def show_settings(self):
        messagebox.showinfo("Configurações", "Aqui estarão as configurações. Como alterar cor, tamanho do tabuleiro, etc.")

if __name__ == "__main__":
    app = PlayerInterface()
    app.root.mainloop()
