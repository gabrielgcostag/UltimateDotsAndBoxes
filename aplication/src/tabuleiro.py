from minijogo import Minijogo
from tkinter import messagebox
from jogador import Jogador

class Tabuleiro:
    def __init__(self, player_Interface):
        self.player_interface = player_Interface
        self.jogadores = [Jogador("1", "blue"), Jogador("2", "red")]
        self.jogadores[0].is_turn = True
        self.minijogos = [[Minijogo(row, col, 3*row + col + 1) for col in range(3)] for row in range(3)]
        self.game_state = "progress"
        self.game_done = False
        self.active_minijogo = None
        self.have_result = False
        self.selecting_minijogo = False
        self.last_filled_box = None

    def create_board(self, canvas):
        for row in self.minijogos:
            for game in row:
                game.create_board(canvas)
                game.draw_tic_tac_toe_grid(canvas)

    # -------------------------------------------------------------- CONNECT DOTS -------------------------------------------------------------- #
    # THIS METHOD IS CALLED WHEN THE PLAYER CLICKS ON THE BOARD
    def connectDots(self, event):
        # This test is used to check if the player got here by clicking on the board or by releasing the mouse button
        if self.active_minijogo:
            if event is None and not self.active_minijogo.line_drawn:
                return

        # 1: Check if it is the local player's turn
        if self.game_state != "progress":
            return
        
        # 2: Check if there is an active minijogo
        if self.active_minijogo is None:
            if event is not None:
                # 2.1: If there is no active minijogo, select one with the click
                active_minijogo = self.findActiveMinijogo(event)
                
                # 2.2.1: If the clicked minijogo is not valid, notify the player
                if not active_minijogo:
                    messagebox.showinfo("Erro", "Selecione um minijogo válido para jogar.")
                    return
                
                # 2.2.2: If the clicked minijogo is valid, set it as active and highlight it 
                self.active_minijogo = active_minijogo
                print(f"Minijogo {self.active_minijogo.id} selecionado.") #TEMPORARIO
                # self.active_minijogo.highlight() # TEM Q IMPLEMENTAR O HIGHLIGHT
                return
            else:
                return
        
        # 3: If there is an active minijogo, draw a line // This effectively calls all the sequence needed for draw line diagram
        play_again = True
        lines = []
        while play_again:
            if event is not None:
                self.active_minijogo.startDrawingLine(event, self.findActivePlayer().color)

            # 3.1: If the line is not drawn, return
            if not self.active_minijogo.line_drawn:
                return
            
            # 3.2: If the line is drawn, save it and create a move dictionary
            if self.active_minijogo.new_line is not None:
                # 4: Create a move dictionary with the drawn line, and reset the attributes pertaining to creation of line from the active minijogo
                move = self.createMoveDictionary(lines, self.active_minijogo.new_line)
                self.active_minijogo.line_drawn = False
                self.active_minijogo.new_line = None

                # 5: Update game state with the move dictionary
                play_again = self.updateGameState(move)

        # 6: Check if the game is done
        self.checkBoardResult(move)


    # --------------------------------------------------------------------------------------------------------------------------------------- #

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

        # 4: Check if a box is filled
        any_box_filled, boxes_coords = modified_minijogo.checkBoxesFilled()

        # 4.1: If no box is filled, set the active minijogo to the last filled box
        if not any_box_filled:
            if self.last_filled_box is not None:
                if self.minijogos[self.last_filled_box[0]][self.last_filled_box[1]].finished == False:
                    self.active_minijogo = self.minijogos[self.last_filled_box[0]][self.last_filled_box[1]]
                else:
                    self.active_minijogo = None
                self.last_filled_box = None

        # 4.2: If any box is filled, update the box matrix
        if any_box_filled:
            self.last_filled_box = boxes_coords[-1]
            for box_coords in boxes_coords:
                modified_minijogo.quadradinhos[box_coords[0]][box_coords[1]].box_filled = True
                modified_minijogo.quadradinhos[box_coords[0]][box_coords[1]].owner = move_maker

            # 4.2: Check if the modified minijogo is finished
            minijogo_done = self.checkMinijogoFinished(modified_minijogo)

            # 4.2.1: Update minijogo owner attributes 
            if not minijogo_done:
                # 4.2.1.1: If the move maker is the active player, allow them to play again
                if move_maker == self.findActivePlayer():
                    play_again = True
                    return play_again
            else:
                self.last_filled_box = None
                modified_minijogo.finished = True
                modified_minijogo.owner = move_maker

                # 4.3: Decide the next active minijogo
                last_filled_box_x = boxes_coords[-1][0]
                last_filled_box_y = boxes_coords[-1][1]

                next_active_minijogo = self.minijogos[last_filled_box_x][last_filled_box_y]

                # 4.4: Check if the next playable minijogo is finished
                # 4.4.1: If it is, set the active minijogo to None
                if next_active_minijogo.finished:
                    self.active_minijogo = None
                # 4.4.2: If it isn't finished, set it as the active minijogo
                else:
                    self.active_minijogo = next_active_minijogo

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
            for player in self.jogadores:
                player.is_turn = not player.is_turn
            move['match_status'] = 'next'
            return move

        # STEP 5.1: Get completed minijogo position in the minijogos matrix
        x = modified_minijogo.id // 3
        y = modified_minijogo.id % 3

        # STEP 5.2: See which player won the minijogo
        p_winner = modified_minijogo.owner

        # STEP 5.3: Check if a player has 3 horizontal minijogos
        if all(self.minijogos[x][i].owner == p_winner for i in range(3)):
            win_condition = True

        # STEP 5.4: Check if a player has 3 vertical minijogos
        elif all(self.minijogos[i][y].owner == p_winner for i in range(3)):
            win_condition = True

        # STEP 5.5: Check if a player has 3 diagonal minijogos (primary diagonal)
        elif x == y and all(self.minijogos[i][i].owner == p_winner for i in range(3)):
            win_condition = True

        # STEP 5.6: Check if a player has 3 diagonal minijogos (secondary diagonal)
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
        
        self.sendmove(move) # TEM Q IMPLEMENTAR O ENVIO DO MOVIMENTO

    # --------------------------------------------------------------------------------------------------------------------------------------- #

    def notify_game_over(self):
        pass

    def sendmove(self, move):
        pass

    def updateUI(self):
        #self.removeHighlights()
        if self.active_minijogo is not None:
            #self.active_minijogo.highlight()
            for row in self.active_minijogo.quadradinhos:
                for quadradinho in row:
                    if quadradinho.owner is None:
                        print("None", end=" ")
                    else:
                        print(4*quadradinho.owner.name[0], end=" ")
                print()
            print()

        #self.updateMinijogoOwnersUI()
        #self.updateBoxOwnersUI()
        #print("UI atualizada.") #TEMPORARIO
        

    def checkMinijogoFinished(self, minijogo):
        minijogo_done = False
        jogadores = {self.jogadores[0].name : 0, self.jogadores[1].name : 0}

        # Count the number of boxes filled by each player
        for row in minijogo.quadradinhos:
            for quadradinho in row:
                if quadradinho.box_filled:
                    jogadores[quadradinho.owner.name] += 1
        
        # Check if a player has 5 boxes filled
        for jogador in jogadores:
            if jogadores[jogador] == 5:
                minijogo_done = True
                break

        return minijogo_done

    def findActiveMinijogo(self, event):
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

    def createMoveDictionary(self, lines, line):
        start_point_index = self.getDotIndex(line[0])
        end_point_index = self.getDotIndex(line[1])

        line = ((start_point_index[0], start_point_index[1]), (end_point_index[0], end_point_index[1]), line[2])
        lines.append(line)

        move = {'match_status' : 'progress', # Obligatory for DOG to understand the message
                'modified_minijogo' : self.active_minijogo.id,
                'lines' : lines,
                'game_done' : False,
                'move_maker' : self.findActivePlayer().name}
        return move

    def findActivePlayer(self):
        for player in self.jogadores:
            if player.is_turn:
                return player
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
    
    def end_game(self):
        pass
