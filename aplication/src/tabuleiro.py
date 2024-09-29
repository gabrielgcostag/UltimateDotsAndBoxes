from minijogo import Minijogo

class Tabuleiro:
    def __init__(self):
        self.minijogos = [[Minijogo(row, col) for col in range(3)] for row in range(3)]

    def create_board(self, canvas):
        for row in self.minijogos:
            for game in row:
                game.create_board(canvas)
                game.draw_tic_tac_toe_grid(canvas)

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