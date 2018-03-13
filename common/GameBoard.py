class GameBoard(object):
    """
        The board of the game, default size is 25x25
    """
    def __init__(self, width, height):
        self.width = width
        self.height = height

        self.gameboard = []
        for i in xrange(width):
            self.gameboard.append([])
            for j in xrange(height):
                self.gameboard[i].append(None)

    def set_object(self, obj, x, y):
        # Add object obj to (x,y)
        self.gameboard[x][y] = obj

    def get_object(self, x, y):
        return self.gameboard[x][y]

    def get_width(self):
        return self.width

    def get_height(self):
        return self.height

    def move_object(self, old_x, old_y, new_x, new_y):
        # Move object from (old_x,old_y) to (new_x,new_y)
        self.gameboard[new_x][new_y] = self.gameboard[old_x][old_y]
        self.gameboard[old_x][old_y] = None

    def del_object(self, x, y):
        #Delete whatever object in coordinate (x,y)
        self.gameboard[x][y] = None
