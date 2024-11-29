from dot import Dot
from box import Box

class Minijogo:
    def __init__(self, section_row, section_col, id):
        self.id = id
        self.dots = []
        self.quadradinhos = []
        self.section_row = section_row
        self.section_col = section_col
        self.board_size = 3
        self.dot_size = 20
        self.margin = 40
        self.spacing = 40

        self.current_line = None
        self.start_point = None
        self.end_point = None
        self.new_line = None

        self.finished = False
        self.line_drawn = False
        self.owner = None
        self.line_valid = False

    def create_board(self, canvas):
        total_dot_size = (3 * self.spacing) + self.dot_size
        offset = (125 - total_dot_size) / 2

        for row in range(4):
            row_points = []
            for col in range(4):
                x = (self.section_col * 200) + self.margin + offset + col * self.spacing
                y = (self.section_row * 200) + self.margin + offset + row * self.spacing
                dot = Dot(x, y, self.dot_size)
                dot.draw(canvas)
                row_points.append(dot)
            self.dots.append(row_points)

        for row in range(3):
            row_boxes = []
            for col in range(3):
                row_boxes.append(Box())
            self.quadradinhos.append(row_boxes)

    def draw_tic_tac_toe_grid(self, canvas):
        grid_size = 600
        canvas.create_line(grid_size // 3, 0, grid_size // 3, grid_size, width=5)
        canvas.create_line(2 * grid_size // 3, 0, 2 * grid_size // 3, grid_size, width=5)

        canvas.create_line(0, grid_size // 3, grid_size, grid_size // 3, width=5)
        canvas.create_line(0, 2 * grid_size // 3, grid_size, 2 * grid_size // 3, width=5)

    def selectNewActiveMinijogo(self, event):
        x_start = self.section_col * 200
        x_end = x_start + 200
        y_start = self.section_row * 200
        y_end = y_start + 200
    
    # Check if the click is within the minijogo's area
        if x_start <= event.x < x_end and y_start <= event.y < y_end:
            # Check if the minijogo is finished
            if not self.finished:
                return self
        
        # Return None if the click is outside the area, or if the minijogo is finished
        return None

    # -------------------------------------------------------------- DRAW LINE -------------------------------------------------------------- #
    def startDrawingLine(self, event, color):
        # 1: Get the nearest point to the click
        self.start_point = self.getNearestPoint(event.x, event.y)
        # 1.1: If the point is valid, select it as the start point
        if self.start_point:
            self.current_line = event.widget.create_line(
                self.start_point.getCenter()[0], self.start_point.getCenter()[1], event.x, event.y, fill=color, width=5)
        # 1.2: If the point is not valid, set line drawn to False and return
        else:
            self.line_drawn = False

    def showLineExtending(self, event):
        # 2: Show the line extending from the start point to the current mouse position
        if self.current_line:
            event.widget.coords(self.current_line, self.start_point.getCenter()[0], self.start_point.getCenter()[1], event.x, event.y)

    def endDrawingLine(self, event):
        if self.current_line:
            # 3: Get the nearest point to the mouse release
            self.end_point = self.getNearestPoint(event.x, event.y)

            # 3.1: If the point is not valid, set line drawn to False
            if not self.end_point:
                self.line_drawn = False
            else:
                # 4: Check if the start and end points are neighbors
                if not self.areNeighbors(self.start_point, self.end_point):
                    self.line_drawn = False
                else:
                    # Update the line coordinates
                    event.widget.coords(self.current_line, self.start_point.getCenter()[0], self.start_point.getCenter()[1], self.end_point.getCenter()[0], self.end_point.getCenter()[1])

                    # 5: Determine line direction and order points
                    if self.start_point.x == self.end_point.x:  # Vertical line
                        direction = 'vertical'
                        if self.start_point.y > self.end_point.y:
                            self.start_point, self.end_point = self.end_point, self.start_point
                    else:  # Horizontal line
                        direction = 'horizontal'
                        if self.start_point.x > self.end_point.x:
                            self.start_point, self.end_point = self.end_point, self.start_point

                    # 5: Check if the line is already drawn
                    already_drawn = self.alreadyDrawn(self.start_point, self.end_point, direction)
                    if already_drawn:
                        self.line_drawn = False
                    else:
                        # 6: Save information about the new line
                        self.saveNewLineInfo(direction)

        # Erase the line visually if it is not valid
        if not self.line_drawn:
            event.widget.delete(self.current_line)

        # Final cleanup, reset line and points
        self.current_line = None
        self.start_point = None
        self.end_point = None
        
    # --------------------------------------------------------------------------------------------------------------------------------------- #

    def saveNewLineInfo(self, direction):
        self.line_drawn = True
        self.new_line = (self.start_point, self.end_point, direction)

    def alreadyDrawn(self, start_point, end_point, direction):
        if direction == 'horizontal':
            if start_point.right and end_point.left:
                return True
        else:
            if start_point.down and end_point.up:
                return True
        return False

    def getNearestPoint(self, x, y):
        tolerance = self.dot_size // 2
        for row_points in self.dots:
            for dot in row_points:
                if dot.isNear(x, y, tolerance):
                    return dot
        return None
    
    def areNeighbors(self, point1, point2):
        point1 = point1.getCenter()
        point2 = point2.getCenter()
        if point1 and point2:
            dist_x = abs(point1[0] - point2[0])
            dist_y = abs(point1[1] - point2[1])
            are_neighbors = (dist_x == self.spacing and dist_y == 0) or (dist_y == self.spacing and dist_x == 0)
            return are_neighbors
        return False

    def saveNewLine(self, line):
        x1y1, x2y2, direction = line
        x1, y1 = x1y1
        x2, y2 = x2y2
        if direction == 'horizontal':
            self.dots[x1][y1].right = True
            self.dots[x2][y2].left = True
        else:
            self.dots[x1][y1].down = True
            self.dots[x2][y2].up = True

    def checkBoxesFilled(self):
        any_filled = False
        filled_boxes = []
        for x in range(3):
            for y in range(3):
                if self.dots [x][y].down and self.dots[x][y].right and self.dots[x+1][y+1].up and self.dots[x+1][y+1].left:
                    if not self.quadradinhos[x][y].box_filled:
                        any_filled = True
                        filled_boxes.append((x, y))
        return any_filled, filled_boxes

    def updateBoxMatrix(self, boxes_coords, move_maker):
        for x, y in boxes_coords:
            self.quadradinhos[x][y].box_filled = True
            self.quadradinhos[x][y].owner = move_maker
        # #TEMPORARIO PARA TESTES
        # for row in self.quadradinhos:
        #     for quadradinho in row:
        #         if quadradinho.getOwner() is None:
        #             print("None", end=" ")
        #         else:
        #             print(4*quadradinho.getOwner().name[0], end=" ")
        #     print()
        # print()

    def checkFinish(self, player):
        print("Minijogo finished test =", sum(quadradinho.getOwner() == player for row in self.quadradinhos for quadradinho in row) >= 5)
        return sum(quadradinho.getOwner() == player for row in self.quadradinhos for quadradinho in row) >= 5
    
    def getOwner(self):
            return self.owner
