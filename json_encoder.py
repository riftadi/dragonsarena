import json
import Character

class CustomEncoder(json.JSONEncoder):
    def default(self, obj): # pylint: disable=E0202
        if isinstance(obj, Character.Character):
            return obj.type

        return json.JSONEncoder.default(self, obj)
