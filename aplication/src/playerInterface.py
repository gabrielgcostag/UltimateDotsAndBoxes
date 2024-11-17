import tkinter as tk
from tkinter import messagebox
from tkinter import ttk
from tkinter import simpledialog
from dog.dog_actor import DogActor
from dog.dog_interface import DogPlayerInterface
from board import Board
from player import Player

class PlayerInterface(DogPlayerInterface):
    def __init__(self):
        self.canvas = None
        self.root = None
        self.enough_players = False
        self.rec_withdrawal = False
        self.rec_move = False
        self.reset = False
        self.board = None
        self.temp = None
        self.start_button = None
        self.dog_server_interface = None

    def start_match(self):
        # 1: Wait for user to start match
        # 2: IF YES, Request match start
        start_status = self.dog_server_interface.start_match(2)
        message = start_status.get_message()
        messagebox.showinfo(message=message)

        # 3: Evaluate response
        if start_status.code != '2':
            self.root.destroy()
            return
        
        # 4: instantiate Board
        self.start_button.destroy()
        self.board = Board(self.temp)
        
        # 5: instantiate Minijogos
        # HAPPENS IN THE BOARD CONSTRUCTOR

        # 6: instantiate Dots AND 7: instantiate Quadradinhos
        self.board.create_board(self.canvas)

        # 8: Get starter from start status
        vez = int(start_status.players[0][2])

        # 9: Update player active status attribute
        self.board.jogadores[vez-1].active = True

    def receive_start(self, start_status):
        message = start_status.get_message()
        messagebox.showinfo(message=message)

        # 1: remove start button
        self.start_button.destroy()

        # 1: Reset the game (USE CASE)
        self.reset_game()

        # 3: Get remote player name from start status
        self.temp[1].name = start_status.players[1][0].capitalize()

        # 4: instantiate Board
        self.board = Board(self.temp)

        # 5: instantiate Minijogos
        # HAPPENS IN THE BOARD CONSTRUCTOR

        # 6: instantiate Dots AND 7: instantiate Quadradinhos
        self.board.create_board(self.canvas)

        # 7: Get starter from start status
        vez = int(start_status.players[0][2])

        # 8: Update player active status attribute
        self.board.jogadores[vez-1].active = True

    def on_press(self, event):
        if self.board:
            self.board.on_press(event)
    
    def on_drag(self, event):
        if self.board:
            self.board.on_drag(event)

    def on_release(self, event):
        if self.board:
            self.board.on_release(event)

    def send_move(self, move):
        self.dog_server_interface.send_move(move)

    def reset_game(self):
        if self.board:
            self.board = None
            for player in self.temp:
                player.active = False

def initialize():
    # 1: instantiate PlayerInterface
    app = PlayerInterface()

    # 2: Request player name
    player_name = simpledialog.askstring(title="Player identification", prompt="Qual o seu nome?")
    app.dog_server_interface = DogActor()

    # 6: Communicate result of connection request
    message = app.dog_server_interface.initialize(player_name, app)
    messagebox.showinfo(message=message)

    # 3: instantiate TKinter elements
    app.root = tk.Tk()
    app.root.title("Jogo")
    app.root.geometry("620x650")
    app.root.resizable(False, False)
    game_frame = tk.Frame(app.root)
    game_frame.pack()
    app.canvas = tk.Canvas(game_frame, width=620, height=620, bg='white')
    app.canvas.pack()
    app.canvas.bind("<ButtonPress-1>", app.on_press)
    app.canvas.bind("<B1-Motion>", app.on_drag)
    app.canvas.bind("<ButtonRelease-1>", app.on_release)
  
    app.start_button = ttk.Button(game_frame, text="Start Game", command=app.start_match)
    app.start_button.place(relx=0.5, rely=0.5, anchor="center", width=200, height=50)
    
    # 4: Instantiate players
    app.temp = [Player("blue"), Player("red")]
    app.temp[0].name = player_name.capitalize()
    
    # 5: create and initialize dog actor
    app.root.mainloop()

if __name__ == "__main__":
    initialize()
