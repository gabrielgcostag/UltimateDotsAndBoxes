from dot import Dot

class Minijogo:
    def __init__(self, section_row, section_col):
        self.section_row = section_row
        self.section_col = section_col
        self.board_size = 3
        self.dot_size = 20
        self.margin = 40
        self.spacing = 40
        self.dots = []

        self.current_line = None
        self.start_point = None
        self.end_point = None

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

    def draw_tic_tac_toe_grid(self, canvas):
        grid_size = 600
        canvas.create_line(grid_size // 3, 0, grid_size // 3, grid_size, width=5)
        canvas.create_line(2 * grid_size // 3, 0, 2 * grid_size // 3, grid_size, width=5)

        canvas.create_line(0, grid_size // 3, grid_size, grid_size // 3, width=5)
        canvas.create_line(0, 2 * grid_size // 3, grid_size, 2 * grid_size // 3, width=5)

    def on_press(self, event):
        self.start_point = self.get_nearest_point(event.x, event.y)
        if self.start_point:
            self.current_line = event.widget.create_line(
                self.start_point[0], self.start_point[1], event.x, event.y, fill="blue", width=5)

    def on_drag(self, event):
        if self.current_line:
            event.widget.coords(self.current_line, self.start_point[0], self.start_point[1], event.x, event.y)

    def on_release(self, event):
        if self.current_line:
            self.end_point = self.get_nearest_point(event.x, event.y, is_droppable=True)
            # if self.end_point and self.are_neighbors(self.start_point, self.end_point):
            if self.end_point:
                event.widget.coords(self.current_line, self.start_point[0], self.start_point[1], self.end_point[0], self.end_point[1])
            else:
                event.widget.delete(self.current_line)
            self.current_line = None
            self.start_point = None
            
    def get_nearest_point(self, x, y, is_droppable=False):
        tolerance = self.dot_size // 2 if not is_droppable else self.dot_size * 1.5
        for row_points in self.dots:
            for dot in row_points:
                if dot.is_near(x, y, tolerance):
                    return dot.get_center()
        return None
    
    #verificacao para entrega 2
    #def are_neighbors(self, point1, point2):
    #    if point1 and point2:
    #        dist_x = abs(point1[0] - point2[0])
    #        dist_y = abs(point1[1] - point2[1])
    #        return (dist_x == self.spacing and dist_y == 0) or (dist_y == self.spacing and dist_x == 0)
    #    return False