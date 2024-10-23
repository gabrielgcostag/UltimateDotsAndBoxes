from minijogo import Minijogo
from tkinter import messagebox

class Tabuleiro:
    def __init__(self, player_Interface):
        self.player_interface = player_Interface
        self.jogadores = []
        self.minijogos = [[Minijogo(row, col, 3*row + col + 1) for col in range(3)] for row in range(3)]
        self.game_state = "progress"
        self.game_done = False
        self.minijogo_completed = 0
        self.active_minijogo = None
        self.have_result = False
        self.selecting_minijogo = False

    def create_board(self, canvas):
        for row in self.minijogos:
            for game in row:
                game.create_board(canvas)
                game.draw_tic_tac_toe_grid(canvas)

    # -------------------------------------------------------------- CONNECT DOTS -------------------------------------------------------------- #
    # THIS METHOD IS CALLED WHEN THE PLAYER CLICKS ON THE BOARD
    def connectDots(self, event):
        # 1: Check if it is the local player's turn
        if self.game_state != "progress":
            return
        
        # 2: Check if there is an active minijogo
        if self.active_minijogo is None:
            # 2.1: If there is no active minijogo, select one with the click
            active_minijogo = self.findActiveMinijogo(event)
            
            # 2.2.1: If there the clicked minijogo is not valid, notify the player
            if not active_minijogo:
                messagebox.showinfo("Erro", "Selecione um minijogo válido para jogar.")
                return
            
            # 2.2.2: If the clicked minijogo is valid, set it as active and highlight it 
            self.active_minijogo = active_minijogo
            print(f"Minijogo {self.active_minijogo.id} selecionado.") #TEMPORARIO
            # self.active_minijogo.highlight() # TEM Q IMPLEMENTAR O HIGHLIGHT
            return
        
        # 3: If there is an active minijogo, draw a line
        self.active_minijogo.startDrawingLine(event)

        # 3.1: If the line is not drawn, return
        if not self.active_minijogo.line_drawn:
            return

        # 4: Create a move dictionary with the drawn line, and reset the attributes pertaining to the line from the active minijogo
        self.createMoveDictionary(self.active_minijogo.new_line)
        self.active_minijogo.line_drawn = False
        self,active_minijogo.new_line = None

    def findActiveMinijogo(self, event):
        for row in self.minijogos:
            for game in row:
                if game.selectNewActiveMinijogo(event):
                    return game
        return None

    def showLineExtending(self, event):
        self.active_minijogo.showLineExtending(event)

    def endDrawingLine(self, event):
        self.active_minijogo.endDrawingLine(event)

    def check_active_minijogo(self):
        if self.active_minijogo is None:
            return False
        return True
    
    def find_minijogo_id(self, id):
        for row in self.minijogos:
            for game in row:
                if game.id == id:
                    return game
        return None
    
    def find_player(self, name):
        for player in self.jogadores:
            if player.nome == name:
                return player
        return None
    
    def end_game(self):
        pass
    
    def update_game_state(self, move):
        play_again = False
        modified_minijogo = self.find_minijogo_id(move['modified_minijogo'])
        move_maker = self.find_player(move['move_maker'])
        lines = move['lines']
        # STEP 4.1: Updating dots matrix
        for line in lines:
            modified_minijogo.save_new_line(line)

        # STEP 4.2: Check if a box is filled
        box_filled, box_coords = modified_minijogo.check_box_filled()

        # STEP 4.3: Update box matrix (OR play_again = False if box not filled)
        if box_filled:
            modified_minijogo.quadradinhos[box_coords[0]][box_coords[1]].box_filled = True
            modified_minijogo.quadradinhos[box_coords[0]][box_coords[1]].owner = move_maker
        else:
            self.player_interface.update_user_interface()
            return False

        # STEP 4.4: Check if a player has 5 boxes
        jogadores = {self.jogadores[0].name : 0, self.jogadores[1].name : 0}
        for box in modified_minijogo.quadradinhos:
            for quadradinho in box:
                if quadradinho.box_filled:
                    jogadores[quadradinho.owner] += 1
        for jogador in jogadores:
            if jogadores[jogador.name] == 5:
                minijogo_done = True
                self.minijogo_completed = modified_minijogo.id
                break

        # STEP 4.5: update minijogo owner attributes (OR play_again = True if minijogo not done)
        if minijogo_done:
            self.active_minijogo.minijogo_done = True
            self.active_minijogo.owner = jogador
        else:
            play_again = True
            self.player_interface.update_user_interface()
            return play_again

        # STEP 4.6: Check if next playable minijogo is active
        if move['next_active_minijogo'] is not None:
            # STEP 4.7: Set next active minijogo (OR set it to None if there is no next active minijogo)
            self.active_minijogo = self.find_minijogo_id(move['next_active_minijogo'])
        else:
            self.active_minijogo = None

        
        # STEP 4.8: Ending update game state method
        self.player_interface.update_user_interface()
        return play_again

    def check_board_result(self, move):
        win_condition = False

        if self.minijogo_completed == 0:
            for player in self.jogadores:
                player.is_turn = not player.is_turn
            move['match_status'] = 'next'
            return move

        # STEP 5.1: Get completed minijogo position in the minijogos matrix
        x = self.minijogo_completed // 3
        y = self.minijogo_completed % 3

        # STEP 5.2: See which player won the minijogo
        p_winner = self.minijogos[x][y].owner

        # STEP 5.3: Check if a player has 3 horizontal minijogos
        if all(self.minijogos[x][i].owner == p_winner for i in range(3)):
            win_condition = True

        # STEP 5.4: Check if a player has 3 vertical minijogos
        elif all(self.minijogos[i][y].owner == p_winner for i in range(3)):
            win_condition = True

        # STEP 5.5: Check if a player has 3 diagonal minijogos (top-left to bottom-right)
        elif x == y and all(self.minijogos[i][i].owner == p_winner for i in range(3)):
            win_condition = True

        # STEP 5.6: Check if a player has 3 diagonal minijogos (top-right to bottom-left)
        elif x + y == 2 and all(self.minijogos[i][2-i].owner == p_winner for i in range(3)):
            win_condition = True

        # STEP 5.7: Check if a player has 5 total minijogos
        elif sum(game.owner == p_winner for row in self.minijogos for game in row) == 5:
            win_condition = True

        # STEP 5.8: Set local game over and update move dictionary according to the result
        if win_condition:
            self.game_done = True
            for player in self.jogadores:
                player.is_turn = False
                if player.name == p_winner:
                    player.is_winner = True
            
            self.notify_game_over() # TEM Q IMPLEMENTAR O AVISO DE GAME OVER

            move['match_status'] = 'finished'
            move['game_done'] = True
        else:
            for player in self.jogadores:
                player.is_turn = not player.is_turn
            move['match_status'] = 'next'
        
        return move
