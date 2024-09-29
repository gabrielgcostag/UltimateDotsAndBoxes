import tkinter as tk
from PIL import Image as ImagePil
from PIL import ImageTk

class DotGame:
    def __init__(self, root, back_to_menu_callback):
        self.root = root
        self.root.resizable(False, False)
        self.canvas = tk.Canvas(root, width=620, height=620, bg='white')
        self.canvas.pack()

        self.background_image = ImagePil.open("aplication/assets/wood_background.jpg")
        self.background_image = self.background_image.resize((620, 620))
        self.background_photo = ImageTk.PhotoImage(self.background_image)
        self.canvas.create_image(0, 0, image=self.background_photo, anchor=tk.NW)

        self.board_size = 3
        self.dot_size = 20
        self.margin = 40
        self.spacing = 40

        self.current_line = None
        self.start_point = None
        self.end_point = None

        self.back_to_menu_callback = back_to_menu_callback

        self.create_menu()
        self.create_board()
        self.draw_tic_tac_toe_grid()

        self.canvas.bind("<ButtonPress-1>", self.on_press)
        self.canvas.bind("<B1-Motion>", self.on_drag)
        self.canvas.bind("<ButtonRelease-1>", self.on_release)

    def create_menu(self):
        menubar = tk.Menu(self.root)
        self.root.config(menu=menubar)

        file_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Menu", menu=file_menu)
        file_menu.add_command(label="Voltar ao Menu Principal", command=self.back_to_menu)

    def create_board(self):
        self.points = []

        total_dot_size = (3 * self.spacing) + self.dot_size
        offset = (125 - total_dot_size) / 2

        for section_row in range(self.board_size):
            for section_col in range(self.board_size):
                section_points = []

                for row in range(4):
                    for col in range(4):
                        x = (section_col * 200) + self.margin + offset + col * self.spacing
                        y = (section_row * 200) + self.margin + offset + row * self.spacing
                        self.canvas.create_oval(x, y, x + self.dot_size, y + self.dot_size, fill="black")
                        section_points.append((x + self.dot_size // 2, y + self.dot_size // 2))
                
                self.points.append(section_points)

    def draw_tic_tac_toe_grid(self):
        grid_size = 600
        self.canvas.create_line(grid_size // 3, 0, grid_size // 3, grid_size, width=5)
        self.canvas.create_line(2 * grid_size // 3, 0, 2 * grid_size // 3, grid_size, width=5)

        self.canvas.create_line(0, grid_size // 3, grid_size, grid_size // 3, width=5)
        self.canvas.create_line(0, 2 * grid_size // 3, grid_size, 2 * grid_size // 3, width=5)

    def on_press(self, event):
        self.start_point = self.get_nearest_point(event.x, event.y)
        if self.start_point:
            self.current_line = self.canvas.create_line(
                self.start_point[0], self.start_point[1], event.x, event.y, fill="blue", width=5)

    def on_drag(self, event):
        if self.current_line:
            self.canvas.coords(self.current_line, self.start_point[0], self.start_point[1], event.x, event.y)

    def on_release(self, event):
        if self.current_line:
            self.end_point = self.get_nearest_point(event.x, event.y, is_droppable=True)
            if self.end_point and self.are_neighbors(self.start_point, self.end_point):
                self.canvas.coords(self.current_line, self.start_point[0], self.start_point[1], self.end_point[0], self.end_point[1])
            else:
                self.canvas.delete(self.current_line)
            self.current_line = None
            self.start_point = None

    def get_nearest_point(self, x, y, is_droppable=False):
        tolerance = self.dot_size // 2 if not is_droppable else self.dot_size * 1.5
        for section_points in self.points:
            for px, py in section_points:
                if abs(px - x) <= tolerance and abs(py - y) <= tolerance:
                    return px, py
        return None

    def are_neighbors(self, point1, point2):
        if point1 and point2:
            dist_x = abs(point1[0] - point2[0])
            dist_y = abs(point1[1] - point2[1])
            return (dist_x == self.spacing and dist_y == 0) or (dist_y == self.spacing and dist_x == 0)
        return False
    
    def back_to_menu(self):
        self.root.destroy()
        self.back_to_menu_callback()