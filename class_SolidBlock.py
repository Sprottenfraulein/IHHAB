class SolidBlock:

    def __init__(self, gameboard, x, y):
        self.gameboard = gameboard
        self.x = x
        self.y = y
        self.width = self.gameboard.square_width
        self.height = self.gameboard.square_height
