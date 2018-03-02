import json
import json_encoder

class GameBoard(object):
    """
        The board of the game, default size is 25x25
    """

    def __init__(self, width=25, height=25):
        self.width = width
        self.height = height
        self.human_count = 0
        self.dragon_count = 0

        self.gameboard = []
        for i in xrange(width):
            self.gameboard.append([])
            for j in xrange(height):
                self.gameboard[i].append(None)

    def set_object(self, obj, x, y):
        """
            Add object obj to (x,y)
        """
        if obj.get_type() == 'h':
            self.human_count += 1
        elif obj.get_type() == 'd':
            self.dragon_count += 1

        self.gameboard[x][y] = obj

    def get_object(self, x=None, y=None):
        if x == None or y == None:
            return json.dumps(self.gameboard, cls=json_encoder.CustomEncoder)
        return self.gameboard[x][y]

    def get_width(self):
        return self.width

    def get_height(self):
        return self.height

    def move_object(self, old_x, old_y, new_x, new_y):
        """
            Move object from (old_x,old_y) to (new_x,new_y)
        """
        self.gameboard[new_x][new_y] = self.gameboard[old_x][old_y]
        self.gameboard[old_x][old_y] = None

    def del_object(self, char_type, x, y):
        """
            Delete whatever object in coordinate (x,y)
        """
        if char_type == 'h':
            self.human_count -= 1
        elif char_type == 'd':
            self.dragon_count -= 1

        self.gameboard[x][y] = None

    def get_human_count(self):
        return self.human_count

    def get_dragon_count(self):
        return self.dragon_count

    def get_list_of(self, c):
        """
            Return list of objects of the specified type c ('h' human or 'd' dragon)
        """
        obj_list = []

        for x in xrange(self.width):
            for y in xrange(self.height):
                obj = self.get_object(x, y)
                if obj != None:
                    if obj.get_type() == c:
                        obj_list.append(obj)

        return obj_list
