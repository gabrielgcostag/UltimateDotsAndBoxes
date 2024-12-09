from minijogo import Minijogo
from tkinter import messagebox
from player import Player
from dot import Dot

class Board:
    def __init__(self, player_Interface):
        self.player_interface = player_Interface
        self.jogadores = player_Interface.temp
        self.minijogos = [[Minijogo(row, col, 3*row + col + 1) for col in range(3)] for row in range(3)]
        self.game_state = ""
        self.move_dict = {}
        self.active_minijogo = self.minijogos[1][1]
        self.last_filled_box = None
        self.canvas = player_Interface.canvas

    def create_board(self, canvas):
        for row in self.minijogos:
            for game in row:
                game.create_board(canvas)
                game.draw_tic_tac_toe_grid(canvas)

    # -------------------------------------------------------------- RECEIVE MOVE -------------------------------------------------------------- #
    def receiveMove(self, move):
        # 1: Check if the game state is waiting for a move from the server
        if self.getGameState() != "wait":
            return
        
        # 2: Update game state with the move dictionary
        play_again = self.updateGameState(move)

        # 3: Check if the game is over
        if move['match_status'] == 'finished':
            # 3.1: Winner decided as the player who made the last move
            winner = self.findPlayer(move['move_maker'])
            # 3.2: Notify local game over
            self.player_interface.notifyGameOver(winner)
        else:
            # Check just to escape KeyError
            if 'next_minijogo' in move:
                # 3.3: Check if the next minijogo is valid
                if move['next_minijogo'] > 0:
                    # 3.3.1: Set the next minijogo as active
                    self.setActiveMinijogo(self.findMinijogoID(move['next_minijogo']))
                else:
                    # 3.3.2: If the next minijogo is invalid, set the active minijogo as None
                    self.active_minijogo = None
            # 3.4: Toggle active player
            self.toggleActivePlayer()
            # 3.5: Update UI
            self.updateUI()

    # -------------------------------------------------------------- CONNECT DOTS -------------------------------------------------------------- #
    # THIS METHOD IS CALLED WHEN THE PLAYER CLICKS ON THE BOARD
    def connectDots(self, click):
        # This test is used to check if the player got here by clicking on the board or by releasing the mouse button
        if self.active_minijogo:
            if click is None and not self.active_minijogo.line_drawn:
                return

        # 1: Check if it is the local player's turn
        if self.getGameState() != "progress":
            return
        
        # 2: Check if there is an active minijogo
        if self.getActiveMinijogo() is None:
            if click is not None:
                # 2.1: If there is no active minijogo, select one with the click
                clicked_minijogo = self.findClickedMinijogo(click)
                
                # 2.2.1: If the clicked minijogo is not valid, notify the player
                if not clicked_minijogo:
                    self.notifyNotValidMinijogo()
                    return
                
                # 2.2.2: If the clicked minijogo is valid, set it as active and highlight it
                self.updateActiveMinijogo(clicked_minijogo)
                self.updateUI()
                return
            else:
                return
        
        # 3: If there is an active minijogo, draw a line // This effectively calls all the sequence needed for draw line diagram
        play_again = True
        while play_again:
            if click is not None:
                self.active_minijogo.startDrawingLine(click, 'blue')

            # 3.1: If the line is not drawn, return
            if not self.active_minijogo.line_drawn:
                return
            
            # 3.2: If the line is drawn, save it and create a move dictionary
            if self.active_minijogo.new_line is not None:
                # 4: Create a move dictionary with the drawn line, and reset the attributes pertaining to creation of line from the active minijogo
                self.createMoveDictionary(self.active_minijogo.new_line)
                self.active_minijogo.line_drawn = False
                self.active_minijogo.new_line = None

                # 5: Update game state with the move dictionary
                play_again = self.updateGameState(self.move_dict)

        # 6: Check if the game is done
        self.checkBoardResult(self.move_dict)

        self.move_dict = {}

    # --------------------------------------------------------------------------------------------------------------------------------------- #

    def getActiveMinijogo(self):
        return self.active_minijogo
    
    def updateActiveMinijogo(self, minijogo):
        self.active_minijogo = minijogo
    
    def notifyNotValidMinijogo(self):
        messagebox.showinfo("Erro", "Selecione um minijogo válido para jogar.")

    # ---------------------------------------------------------- UPDATE GAME STATE ---------------------------------------------------------- #
    # THIS METHOD IS CALLED INSIDE THE CONNECT DOTS AND RECEIVE MOVE METHODS
    def updateGameState(self, move):
        play_again = False

        # 1: Unpack move dictionary
        move_maker = self.findPlayer(move['move_maker'])
        lines = move['lines']

        # 2: Detect modified minijogo
        modified_minijogo = self.findMinijogoID(move['modified_minijogo'])

        # 3: Updating dots matrix
        for line in lines:
            modified_minijogo.saveNewLine(line)
            if move['match_status'] == 'next':
                modified_minijogo.drawVisualLine(self.canvas, line)

        # 4: Check if a box is filled
        any_box_filled ,boxes_coords = modified_minijogo.checkBoxesFilled()

        # 4.1: If no box is filled, set the active minijogo to the last filled box
        if not any_box_filled:
            next = self.decideNewActiveMinijogo()
                
            if next is not None:
                self.move_dict['next_minijogo'] = next.id
            else:
                self.move_dict['next_minijogo'] = -1

        # 4.2: If any box is filled, update the box matrix
        else:
            self.last_filled_box = boxes_coords[-1]
            modified_minijogo.updateBoxMatrix(boxes_coords, move_maker)

            # 4.2: Check if the modified minijogo is finished
            minijogo_done = modified_minijogo.checkFinish(self.findActivePlayer())

            # 4.2.1: Update minijogo owner attributes 
            if not minijogo_done:
                # 4.2.1.1: If the move maker is the active player, allow them to play again
                if move_maker == self.findActivePlayer():
                    play_again = True
            else:
                modified_minijogo.owner = move_maker
                modified_minijogo.finished = True

                # 4.3: Decide the next active minijogo
                next_active_minijogo = self.decideNewActiveMinijogo()
                if next_active_minijogo is not None:
                    self.move_dict['next_minijogo'] = next_active_minijogo.id
                else:
                    self.move_dict['next_minijogo'] = -1

        # STEP 4.5: Ending update game state method
        self.updateUI()
        return play_again

    # --------------------------------------------------------------------------------------------------------------------------------------- #

    # ---------------------------------------------------------- CHECK BOARD RESULT --------------------------------------------------------- #
    def checkBoardResult(self, move):
        win_condition = False
        modified_minijogo = self.findMinijogoID(move['modified_minijogo'])

        # If no minijogo was completed, toggle active player, modify move dictionary and return
        if modified_minijogo.finished == False:
            self.toggleActivePlayer()
            move['match_status'] = 'next'

        else:
            # STEP 5.1: Get completed minijogo position in the minijogos matrix
            x, y = self.getCoordsFromID(modified_minijogo.id)

            # STEP 5.2: See which player won the minijogo
            p_winner = modified_minijogo.getOwner()

            # STEP 5.3: Check if a player has 3 horizontal minijogos
            if all(self.minijogos[x][i].getOwner() == p_winner for i in range(3)):
                win_condition = True

            # STEP 5.4: Check if a player has 3 vertical minijogos
            elif all(self.minijogos[i][y].getOwner() == p_winner for i in range(3)):
                win_condition = True

            # STEP 5.5: Check if a player has 3 diagonal minijogos (primary diagonal)
            elif x == y and all(self.minijogos[i][i].getOwner() == p_winner for i in range(3)):
                win_condition = True

            # STEP 5.6: Check if a player has 3 diagonal minijogos (secondary diagonal)
            elif x + y == 2 and all(self.minijogos[i][2-i].getOwner() == p_winner for i in range(3)):
                win_condition = True

            # STEP 5.7: Check if a player has 5 total minijogos
            elif sum(game.getOwner() == p_winner for row in self.minijogos for game in row) == 5:
                win_condition = True

            # STEP 5.8: Set local game over and update move dictionary according to the result
            if win_condition:
                move = self.endLocalGame(move, p_winner)
                self.player_interface.notifyGameOver(p_winner)

            else:
                self.toggleActivePlayer()
                self.updateUI()
                move['match_status'] = 'next'

        self.player_interface.send_move(move)

    # --------------------------------------------------------------------------------------------------------------------------------------- #

    def getGameState(self):
        return self.game_state

    def toggleActivePlayer(self):
        self.last_filled_box = None
        if self.getGameState() == "progress":
            self.game_state = "wait"
        elif self.getGameState() == "wait":
            self.game_state = "progress"

    def endLocalGame(self, move, winner):
        self.game_state = "finished"
        for player in self.jogadores:
            if player == winner:
                player.is_winner = True

        move['match_status'] = 'finished'
        return move

    def getCoordsFromID(self, id):
        id -= 1
        return id // 3, id % 3
    
    def updateUI(self):
        self.canvas.delete("highlight")
        self.canvas.delete("turn_indicator")
        if self.active_minijogo is not None:
             if self.active_minijogo:
                x_start = self.active_minijogo.section_col * 200
                y_start = self.active_minijogo.section_row * 200
                self.canvas.create_rectangle(x_start, y_start, x_start + 200, y_start + 200, outline="red", width=5, tags="highlight")
        for row in self.minijogos:
            for game in row:
                if game.owner:
                    x_start = game.section_col * 200
                    y_start = game.section_row * 200
                    if game.owner.color == "blue":
                        self.canvas.create_line(x_start, y_start, x_start + 200, y_start + 200, fill="blue", width=10)
                        self.canvas.create_line(x_start + 200, y_start, x_start, y_start + 200, fill="blue", width=10)
                    else:
                        self.canvas.create_oval(x_start, y_start, x_start + 200, y_start + 200, outline="red", width=10)
        for row in self.minijogos:
            for game in row:
                for i in range(3):
                    for j in range(3):
                        box = game.quadradinhos[i][j]
                        if box.owner:
                            x_start = game.section_col * 200 + 40 + j * 40
                            y_start = game.section_row * 200 + 40 + i * 40
                            if box.owner.color == "blue":
                                self.canvas.create_line(x_start, y_start, x_start + 40, y_start + 40, fill="blue", width=5)
                                self.canvas.create_line(x_start + 40, y_start, x_start, y_start + 40, fill="blue", width=5)
                            else:
                                self.canvas.create_oval(x_start, y_start, x_start + 40, y_start + 40, outline="red", width=5)
        
    def findClickedMinijogo(self, event):
        for row in self.minijogos:
            for game in row:
                if game.selectNewActiveMinijogo(event):
                    return game
        return None

    def divideReleaseExecution(self, event):
        # This method is called when the player releases the mouse button
        self.endDrawingLine(event)
        # This is used to update the game state as soon as the player releases the mouse button
        self.connectDots(None)

    def showLineExtending(self, event):
        if not self.active_minijogo:
            return
        self.active_minijogo.showLineExtending(event)

    def endDrawingLine(self, event):
        if not self.active_minijogo:
            return
        self.active_minijogo.endDrawingLine(event)

    def createMoveDictionary(self, line):
        start_point_index = self.getDotIndex(line[0])
        end_point_index = self.getDotIndex(line[1])

        line = ((start_point_index[0], start_point_index[1]), (end_point_index[0], end_point_index[1]), line[2])

        # Initialize or update the move dictionary
        if len(self.move_dict) <= 1:  # Check if move is empty
            self.move_dict['match_status'] = 'progress'
            self.move_dict['modified_minijogo'] = self.active_minijogo.id
            self.move_dict['lines'] = [line]
            self.move_dict['move_maker'] = self.findActivePlayer().name
        else:
            self.move_dict['lines'].append(line)

    def findActivePlayer(self):
        if self.game_state == "progress":
            return self.jogadores[0]
        elif self.game_state == "wait":
            return self.jogadores[1]
        return None

    def getDotIndex(self, dot):
        for x in range(4):
            for y in range(4):
                if self.active_minijogo.dots[x][y] == dot:
                    return (x,y)

    def check_active_minijogo(self):
        if self.active_minijogo is None:
            return False
        return True
    
    def findMinijogoID(self, id):
        for row in self.minijogos:
            for game in row:
                if game.id == id:
                    return game
        return None
    
    def findPlayer(self, name):
        for player in self.jogadores:
            if player.name == name:
                return player
        return None
    
    def decideNewActiveMinijogo(self):
        if self.last_filled_box is not None:
            if self.minijogos[self.last_filled_box[0]][self.last_filled_box[1]].finished == False:
                return self.minijogos[self.last_filled_box[0]][self.last_filled_box[1]]
            else:
                return None
        return self.active_minijogo
    
    def setGameState(self, state):
        self.game_state = state

    def setActiveMinijogo(self, minijogo):
        self.active_minijogo = minijogo


    """
    DIVISÃO DE FUNCIONALIDADES EM MÉTODOS DO updateUI:

    def updateUI(self):
        self.removeHighlights()
        if self.active_minijogo is not None:
            self.highlight()
        self.updateMinijogoOwnersUI()
        self.updateBoxOwnersUI()
        self.updateTurnIndicator()

    def highlight(self):
        if self.active_minijogo:
            x_start = self.active_minijogo.section_col * 200
            y_start = self.active_minijogo.section_row * 200
            self.canvas.create_rectangle(x_start, y_start, x_start + 200, y_start + 200, outline="red", width=5, tags="highlight")

    def removeHighlights(self):
        self.canvas.delete("highlight")
    
    def updateBoxOwnersUI(self):
        for row in self.minijogos:
            for game in row:
                for i in range(3):
                    for j in range(3):
                        box = game.quadradinhos[i][j]
                        if box.owner:
                            x_start = game.section_col * 200 + 40 + j * 40
                            y_start = game.section_row * 200 + 40 + i * 40
                            if box.owner.color == "blue":
                                self.canvas.create_line(x_start, y_start, x_start + 40, y_start + 40, fill="blue", width=5)
                                self.canvas.create_line(x_start + 40, y_start, x_start, y_start + 40, fill="blue", width=5)
                            else:
                                self.canvas.create_oval(x_start, y_start, x_start + 40, y_start + 40, outline="red", width=5)
    
    def updateMinijogoOwnersUI(self):
        for row in self.minijogos:
            for game in row:
                if game.owner:
                    x_start = game.section_col * 200
                    y_start = game.section_row * 200
                    if game.owner.color == "blue":
                        self.canvas.create_line(x_start, y_start, x_start + 200, y_start + 200, fill="blue", width=10)
                        self.canvas.create_line(x_start + 200, y_start, x_start, y_start + 200, fill="blue", width=10)
                    else:
                        self.canvas.create_oval(x_start, y_start, x_start + 200, y_start + 200, outline="red", width=10)
                        
    def updateTurnIndicator(self):
        active_player = self.findActivePlayer()
        if active_player:
            next_player_turn = 'Red' if active_player.color == 'blue' else 'Blue'
            turn_text = f"Turn: {next_player_turn}"
            self.canvas.create_text(10, 10, anchor="nw", text=turn_text, fill=next_player_turn, font=("Arial", 16), tags="turn_indicator")"""