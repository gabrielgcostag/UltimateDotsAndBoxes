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
        canvas.bind("<ButtonRelease-1>", self.board.endDrawingLine)

        game_root.mainloop()

    def back_to_menu(self, game_root):
        game_root.destroy()

    def update_game_state(self, move):
        modified_minijogo = self.board.find_minijogo_id(move['modified_minijogo'])
        lines = move['lines']
        for line in lines:
            modified_minijogo.draw_line(line)

 # --------------------------------------------------------------- INITIALIZE --------------------------------------------------------------- #
    # THIS METHOD HAS TO BE CALLED WHEN THE USER RUNS THE PROGRAM
    def initialize(self):
        # First step: Instantiate Tkinter Elements

        # Second step: Ask for player identification
        player_name = "diego" #simpledialog.askstring("Nome do Jogador", "Digite seu nome:")

 # -------------------------------------------------------------- CONNECT DOTS -------------------------------------------------------------- #
    # THIS METHOD HAS TO BE CALLED WHEN THE PLAYER CLICKS AND DRAGS THE MOUSE TO DRAW A LINE
    def connect_dots(self):
        play_again = True
        lines = []

        # First step: GUARANTEE THERE IS AN ACTIVE MINIJOGO (use case)
        while not self.board.check_active_minijogo():
            messagebox.showinfo("Erro", "Selecione um minijogo válido para jogar.")
            self.board.on_press(None, selecting_minijogo=True)
        self.board.highlight_active_minijogo()

        while play_again:
            # Second step: DRAW LINE
            # This part is implemented directly in the Tabuleiro class, as it is a GUI interaction //PRECISO TIRAR DÚVIDAS COM O GABRIEL
            # Ther coords of the drawn line will be stored as ints in the line_drawn_int variable
            line_drawn_int = (('coord_x', 'coord_y', 'direction'), ('coord_x', 'coord_y', 'direction'))

            # Third step: CREATE MOVE DICTIONARY
            lines.append(line_drawn_int)
            for jogador in self.board.jogadores:
                if jogador.is_turn:
                    move_maker = jogador.nome
                    break
            
            move = {'match_status' : 'progress', # Obligatory for DOG to understand the message
                    'modified_minijogo' : self.board.active_minijogo.id,
                    'lines' : lines,
                    'next_active_minijogo' : None,
                    'game_done' : False,
                    'move_maker' : move_maker}
            
            # Fourth step: UPDATE GAME STATE (use case)
            play_again = self.board.update_game_state(move)

        # Fifth step: CHECK BOARD RESULT
        move = self.board.check_board_result(move)
        self.dog_server_interface.send_move(move)

 # ------------------------------------------------------------------------------------------------------------------------------------------ #

if __name__ == "__main__":
    # main function will describe the flow of the program as described by the Interaction Overview Diagram
    # Instantiate the PlayerInterface class and run the mainloop outside of initialize method
    app = PlayerInterface()
