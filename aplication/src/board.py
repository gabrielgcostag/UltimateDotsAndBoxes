from minijogo import Minijogo

class Board:
    def __init__(self, jogadores):
        self.jogadores = jogadores
        self.minijogos = [[Minijogo(row, col) for col in range(3)] for row in range(3)]
        self.minijogos[1][1].minijogo_active = True
        self.game_state = ""
        self.game_done = False
        self.active_minijogo = None
        self.have_result = False

    def create_board(self, canvas):
        for row in self.minijogos:
            for game in row:
                game.create_minijogo(canvas)
                game.draw_tic_tac_toe_grid(canvas)
                game.create_boxes()

    def on_press(self, event):
        for row in self.minijogos:
            for game in row:
                game.on_press(event)

    def on_drag(self, event):
        for row in self.minijogos:
            for game in row:
                game.on_drag(event)

    def on_release(self, event):
        for row in self.minijogos:
            for game in row:
                game.on_release(event)
