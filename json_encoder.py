import json

import GameState
import GameBoard
import Character

class GameStateEncoder(json.JSONEncoder):
    def default(self, obj): # pylint: disable=E0202
        if isinstance(obj, GameState.GameState):
            return [x for x in obj.get_characters() if x.hp > 0]

        if isinstance(obj, Character.Character):
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
        self.gb = GameBoard.GameBoard(25,25)

    def parse(self, json_str):
        character_list = json.loads(json_str)
        if len(character_list) > 0:
            character_list = map(self.createCharacter, character_list)

        for character in character_list:
            self.gb.set_object(character,character.x, character.y)

        state = GameState.GameState()
        state.set_characters_list(character_list)
        state.set_gameboard(self.gb)
        return state

    def createCharacter(self, char):
        if char["type"] == "h":
            return Character.Human(char["id"], char["id"],self.gb,char["hp"],0,char["x"], char['y'], False)
        else:
            return Character.Dragon(char["id"], char["id"],self.gb,char["hp"],0,char["x"], char['y'], False)

