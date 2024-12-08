from tkinter import messagebox
from dog.dog_interface import DogPlayerInterface

from board import Board

class PlayerInterface(DogPlayerInterface):
    def __init__(self):
        self.board = None
        self.canvas = None
        self.root = None
        self.start_button = None
        self.dog_server_interface = None
        self.temp = None

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

    def notifyGameOver(self, winner):
        messagebox.showinfo(message="O jogo acabou. O vencedor é: " + winner.name)

    def exit(self):
        self.root.destroy()

    # ------------------------------------------------- RECEIVE WITHDRAWAL NOTIFICATION --------------------------------------------------------- #
    def receive_withdrawal_notification(self):
        # 1: Display withdrawal notification
        messagebox.showinfo(message="O oponente abandonou a partida.")
        # 2: Close the game
        self.root.destroy()

    # --------------------------------------------------------------- RESET GAME --------------------------------------------------------------- #
    def reset_game(self):
        # 1: Check if board is instantiated
        if self.board:
            # 2: Remove board from PlayerInterface
            self.board = None

    # --------------------------------------------------------------- START MATCH --------------------------------------------------------------- #
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
        
        # 4: remove start button
        self.start_button.destroy()

        # 5: get remote player name from start status
        self.temp[1].set_name(start_status.players[1][0].capitalize())

        # 6: instantiate Board
        self.board = Board(self)

        # 7: instantiate Minijogos
        # HAPPENS IN THE BOARD CONSTRUCTOR

        # 8: Bind canvas events
        self.canvas.bind("<ButtonPress-1>", self.board.connectDots)
        self.canvas.bind("<B1-Motion>", self.board.showLineExtending)
        self.canvas.bind("<ButtonRelease-1>", self.board.divideReleaseExecution)

        # 9: instantiate Dots AND 10: instantiate Boxes
        self.board.create_board(self.canvas)

        # 11: Get starter from start status
        vez = int(start_status.players[0][2])
        options = {1: "progress", 2: "wait"}
        self.board.SetGameState(options[vez])

        #12: Update user interface
        self.board.updateUI()

    # --------------------------------------------------------------- RECEIVE START --------------------------------------------------------------- #
    def receive_start(self, start_status):
        # 1: Display start message
        message = start_status.get_message()
        messagebox.showinfo(message=message)

        # 2: remove start button
        self.start_button.destroy()

        # 3: Reset the game (USE CASE)
        self.reset_game()

        # 4: Get remote player name from start status
        self.temp[1].set_name(start_status.players[1][0].capitalize())

        # 5: instantiate Board
        self.board = Board(self)

        # 6: instantiate Minijogos
        # HAPPENS IN THE BOARD CONSTRUCTOR

        # 7: Bind Tk canvas events
        self.canvas.bind("<ButtonPress-1>", self.board.connectDots)
        self.canvas.bind("<B1-Motion>", self.board.showLineExtending)
        self.canvas.bind("<ButtonRelease-1>", self.board.divideReleaseExecution)

        # 8: instantiate Dots AND 9: instantiate Quadradinhos
        self.board.create_board(self.canvas)

        # 10: Set starter from start status
        vez = int(start_status.players[0][2])
        options = {1: "progress", 2: "wait"}
        self.board.SetGameState(options[vez])

        #11: Update user interface
        self.board.updateUI()

    # --------------------------------------------------------------- RECEIVE MOVE --------------------------------------------------------------- #
    def receive_move(self, move):
        self.board.receiveMove(move)
