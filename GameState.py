from GameBoard import GameBoard

class GameState(object):
    """
        Container class for characters and gameboard
    """
    def __init__(self, width=25, height=25):
        self.gb = GameBoard(width, height)
        self.character_list = []
        self.action_list = []

        # action_dict = {10001 : {'action_type' : 'spawn', 'msg_id' : 10001, ...},
        #                10002 : {'action_type' : 'move', 'msg_id' : 10002, ...},}

    def get_characters(self):
        return self.character_list

    def set_characters_list(self, list):
        self.character_list = list

    def set_gameboard(self, gb):
        self.gb = gb

    def add_character(self, obj):
        self.character_list.append(obj)

    def get_actions(self):
        return self.action_list

    def get_gameboard(self):
        return self.gb

    def get_object(self, x, y):
        return self.gb.get_object(x, y)

    def add_action(self, action):
        """
            Save action in a dictionary where the keys are msg_id
        """
        self.action_list.append(action)

    def get_action_id(self, msg_id):
        """
            Retrieve action where the key is msg_id, give None if msg not found
        """
        result = None
        for action in self.action_list:
            if action["msg_id"] == msg_id:
                result = action
                break

        return result

    def get_object_by_id(self, obj_id):
        result = None
        for char in self.character_list:
            if char.get_obj_id() == obj_id:
                result = char
                break

        return result
