class Dot:
    def __init__(self, x, y, size=20):
        self.x = x
        self.y = y
        self.up = False
        self.down = False
        self.left = False
        self.right = False
        self.size = size

    def draw(self, canvas):
        canvas.create_oval(self.x, self.y, self.x + self.size, self.y + self.size, fill="black")

    def isNear(self, x, y, tolerance):
        return abs(self.x + self.size // 2 - x) <= tolerance and abs(self.y + self.size // 2 - y) <= tolerance

    def getCenter(self):
        return self.x + self.size // 2, self.y + self.size // 2
