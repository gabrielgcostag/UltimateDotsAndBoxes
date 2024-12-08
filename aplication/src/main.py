import tkinter as tk
from tkinter import messagebox
from tkinter import ttk
from tkinter import simpledialog
from dog.dog_actor import DogActor

from playerInterface import PlayerInterface
from player import Player
# --------------------------------------------------------------- INITIALIZE --------------------------------------------------------------- #
# THIS METHOD HAS TO BE CALLED WHEN THE USER RUNS THE PROGRAM
def initialize():
    # 1: instantiate PlayerInterface
    app = PlayerInterface()

    # 2: instantiate TKinter elements
    app.root = tk.Tk()
    app.root.title("Jogo")
    app.root.geometry("620x650")
    app.root.resizable(False, False)

    top_frame = tk.Frame(app.root)
    top_frame.pack(side=tk.TOP, fill=tk.X, pady=5)

    back_button = ttk.Button(top_frame, text="Exit", command=lambda: app.exit(), width=10)
    back_button.pack(side=tk.LEFT, padx=5)

    game_frame = tk.Frame(app.root)
    game_frame.pack()

    app.canvas = tk.Canvas(game_frame, width=620, height=620, bg='white')
    app.canvas.pack()

    app.start_button = ttk.Button(game_frame, text="Start Game", command=app.start_match)
    app.start_button.place(relx=0.5, rely=0.5, anchor="center", width=200, height=50)
    
    # 3: Instantiate players
    app.temp = [Player("blue"), Player("red")]

    # 4: Request player name
    player_name = simpledialog.askstring(title="Player identification", prompt="Qual o seu nome?")
    if player_name:
        app.temp[0].set_name(player_name.capitalize())
    
    # 5: create and initialize dog actor
    app.dog_server_interface = DogActor()

    # 6: Communicate result of connection request
    message = app.dog_server_interface.initialize(player_name, app)
    messagebox.showinfo(message=message)

    # 7: Run mainloop
    app.root.mainloop()

# ------------------------------------------------------------------------------------------------------------------------------------ #

if __name__ == "__main__":
    # main function will describe the flow of the program as described by the Interaction Overview Diagram
    # Instantiate the PlayerInterface class and run the mainloop outside of initialize method
    initialize()
