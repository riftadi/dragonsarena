import json

from common.GameState import GameState
from common.GameBoard import GameBoard
from common.Character import *

class GameStateEncoder(json.JSONEncoder):
    def default(self, obj): # pylint: disable=E0202
        if isinstance(obj, GameState):
            return [x for x in obj.get_characters() if x.hp > 0]

        if isinstance(obj, Character):
            return {
                "id": obj.obj_id,
                "x": obj.x,
                "y": obj.y,
                "hp": obj.hp,
                "type": obj.type
            }

        return json.JSONEncoder.default(self, obj)

class GameStateParser():
    def __init__(self):
        self.gb = GameBoard(25,25)

    def parse(self, json_str):
        status_chlist = json.loads(json_str)
        game_running_flag = status_chlist["is_running"]
        character_list = status_chlist["gamestate"]

        if len(character_list) > 0:
            character_list = map(self.createCharacter, character_list)

        for character in character_list:
            self.gb.set_object(character,character.x, character.y)

        state = GameState()
        state.set_characters_list(character_list)
        state.set_gameboard(self.gb)
        
        return game_running_flag, state

    def createCharacter(self, char):
        if char["type"] == "h":
            return Human(char["id"], char["id"],char["hp"],0,char["x"], char["y"], False)
        else:
            return Dragon(char["id"], char["id"],char["hp"],0,char["x"], char["y"], False)

