from threading import Thread
import pygame
import json

from json_encoder import GameStateEncoder, GameStateParser

from GameBoard import GameBoard
from GameState import GameState
from UnifiedMessageBox import UnifiedMessageBox
from Character import *

class TSSEngine(Thread):
    def __init__(self, width, height, msg_box, clockrate=20, verbose=True):
        Thread.__init__(self)
        self.width = width
        self.height = height
        self.msg_box = msg_box
        self.clockrate = clockrate
        self.verbose = verbose

        self.leadingstate = GameState(width, height)
        # --TODO-- add more trailing state
        # self.trailingstate01board = GameBoard(width, height)
        # self.trailingstate02board = GameBoard(width, height)

        self.game_timer = 0
        self.game_running_flag = True
        self.last_msg_box_access_time = 0

        self.dragons_joined = 0
        self.humans_joined = 0

        self.trailing_timer1 = -100

        self.human_count = 0
        self.dragon_count = 0

    def run(self):
        while self.is_game_running():
            # read message buffer
            mb = self.get_message_box()
            action_list = mb.get_messages(self.last_msg_box_access_time, self.game_timer)

            self.process_action_list(action_list)

            self.last_msg_box_access_time = self.game_timer
            pygame.time.wait(self.clockrate)
            self.game_timer += self.clockrate

            # publish current gamestate
            json_str = json.dumps(self.leadingstate, cls=GameStateEncoder)
            self.msg_box.send_message(json_str, "gamestate")

            # clear message_box every 300 ms
            if self.game_timer % 300 == 0:
                mb.delete_messages_before(self.game_timer)

        self.msg_box.send_message("Over", "game over")

    def get_list_of(self, c):
        return self.leadingstate.get_gameboard().get_list_of(c)

    def get_gameboard(self):
        return self.leadingstate.get_gameboard()

    def process_action_list(self, action_list):
        for action in action_list:
            # save it for checking purpose in the trailing states
            self.leadingstate.add_action(action)

            # based on message type, do action
            msg_id = action["msg_id"]
            timestamp = action["timestamp"]
            action_type = action["type"]
            #server_id = action["#server_id"]
            obj_id = action["player_id"]

            # now do the action
            if action_type == "spawn":
                # create a new character
                obj_name = "name" #action["obj_name"]
                obj_type = action["player_type"]

                new_obj = None
                if obj_type == 'human':
                    self.humans_joined += 1
                    new_obj = Human(obj_id, obj_name, self.leadingstate.get_gameboard(),
                        verbose=self.verbose)
                elif obj_type == 'dragon':
                    self.dragons_joined += 1
                    new_obj = Dragon(obj_id, obj_name, self.leadingstate.get_gameboard(),
                        verbose=self.verbose)

                self.leadingstate.add_character(new_obj)

            elif action_type == "move":
                # move a character
                #server_id = action["#server_id"]

                obj_id = action["player_id"]

                x = action["x"]
                y = action["y"]

                obj = self.leadingstate.get_object_by_id(obj_id)
                obj.move_to(x,y)

            elif action_type == "attack":
                # attack a character
                #server_id = action["#server_id"]

                obj_id = action["player_id"]
                target_id = action["target_id"]

                obj = self.leadingstate.get_object_by_id(obj_id)
                target_obj = self.leadingstate.get_object_by_id(target_id)
                target_obj.get_attacked(obj.get_ap(), obj.get_name())

            elif action_type == "heal":
                # heal a character
                #server_id = action["#server_id"]

                obj_id = action["obj_id"]
                target_id = action["target_id"]

                obj = self.leadingstate.get_object_by_id(obj_id)
                target_obj = self.leadingstate.get_object_by_id(target_id)
                target_obj.get_healed(obj.get_ap(), obj.get_name())

    def get_current_time(self):
        return self.game_timer

    def get_message_box(self):
        return self.msg_box

    def get_object(self, x=None, y=None):
        return self.leadingstate.get_object(x,y)

    def get_width(self):
        return self.width

    def get_height(self):
        return self.height

    def get_current_time(self):
        return self.game_timer

    def is_game_running(self):
        return not self.is_game_finished()

    def stop_game(self):
        self.game_running_flag = False

    def move_object(self, old_x, old_y, new_x, new_y):
        gb = self.leadingstate.get_gameboard()
        gb[new_x][new_y] = gb[old_x][old_y]
        gb[old_x][old_y] = None

    def get_object_by_id(self, obj_id):
        result = None
        gb = self.leadingstate.get_gameboard()

        for x in xrange(gb.get_width()):
            for y in xrange(gb.get_height()):
                obj = gb.get_object(x,y)
                if obj != None and obj.get_obj_id() == obj_id:
                    result = gb.get_object(x,y)
                    break

        return result

    def is_game_finished(self):
        gb = self.leadingstate.get_gameboard()

        if self.dragons_joined < 1 or self.humans_joined < 1:
            return False

        if gb.get_dragon_count() <= 0 and gb.get_human_count() > 0:
            print "humans win!"
            return True
        elif gb.get_dragon_count() > 0 and gb.get_human_count() <= 0:
            print "dragons win!"
            return True

        return False
