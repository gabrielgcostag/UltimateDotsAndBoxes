import tkinter as tk
from tkinter import messagebox
from tkinter import ttk
from tkinter import simpledialog
from tabuleiro import Tabuleiro
from PIL import Image, ImageTk

class PlayerInterface():
    def __init__(self):
        self.board = None
        self.initialize()
        self.start_game()

    def start_game(self):
        game_root = tk.Tk()
        game_root.title("Jogo")
        game_root.geometry("620x650")
        game_root.resizable(False, False)

        top_frame = tk.Frame(game_root)
        top_frame.pack(side=tk.TOP, fill=tk.X, pady=5)

        back_button = ttk.Button(top_frame, text="Exit", command=lambda: self.back_to_menu(game_root), width=10)
        back_button.pack(side=tk.LEFT, padx=5)

        game_frame = tk.Frame(game_root)
        game_frame.pack()

        canvas = tk.Canvas(game_frame, width=620, height=620, bg='white')
        canvas.pack()

        original_image = Image.open("assets/wood_background.jpg")
        resized_image = original_image.resize((620, 620))
        self.background_image = ImageTk.PhotoImage(resized_image)
        canvas.create_image(0, 0, anchor=tk.NW, image=self.background_image)

        self.board = Tabuleiro(self)
        self.board.create_board(canvas)

        canvas.bind("<ButtonPress-1>", self.board.connectDots)
        canvas.bind("<B1-Motion>", self.board.showLineExtending)
        canvas.bind("<ButtonRelease-1>", self.board.divideReleaseExecution)

        game_root.mainloop()

    def back_to_menu(self, game_root):
        game_root.destroy()

    def notifyGameOver(self, winner):
        messagebox.showinfo("Game Over", "O jogador " + winner.name + " venceu!")

    def sendMove(self, move):
        pass

 # --------------------------------------------------------------- INITIALIZE --------------------------------------------------------------- #
    # THIS METHOD HAS TO BE CALLED WHEN THE USER RUNS THE PROGRAM
    def initialize(self):
        # First step: Instantiate Tkinter Elements

        # Second step: Ask for player identification
        player_name = "diego" #simpledialog.askstring("Nome do Jogador", "Digite seu nome:")

if __name__ == "__main__":
    # main function will describe the flow of the program as described by the Interaction Overview Diagram
    # Instantiate the PlayerInterface class and run the mainloop outside of initialize method
    app = PlayerInterface()
