from threading import Thread
import pygame
import json

from common.GameState import GameState
from common.Character import *

### --TODO-- THIS CLASS IS NOT WORKER CLASS, SO NO THREAD BELONG HERE
class TSSModel(object):
    def __init__(self, width, height, verbose=True):
        self.width = width
        self.height = height
        self.verbose = verbose

        self.leadingstate = GameState(width, height)
        # --TODO-- add more trailing state
        # self.trailingstate01board = GameState(width, height)
        # self.trailingstate02board = GameState(width, height)

        # THE ABSOLUTE SOURCE OF TRUTH OF GAME RUNNING STATE
        # It should be True if running, False if not running
        self.game_running_flag = True

        # game timer in milliseconds
        self.game_timer = 0
        self.last_msg_box_access_time = 0

        self.dragons_joined = 0
        self.humans_joined = 0

        self.trailing_timer1 = -100

        self.human_count = 0
        self.dragon_count = 0

        self.players_and_dragons_have_spawned_flag = False

    # def run(self):
    #     while self.is_game_running():
    #         # read message buffer
    #         mb = self.get_message_box()
    #         action_list = mb.get_messages(self.last_msg_box_access_time, self.game_timer)

    #         self.process_action_list(action_list)

    #         self.last_msg_box_access_time = self.game_timer
    #         pygame.time.wait(self.clockrate)
    #         self.game_timer += self.clockrate

    #         # publish current gamestate
    #         # json_str = json.dumps(self.leadingstate, cls=GameStateEncoder)
    #         # self.msg_box.send_message(json_str, "gamestate")

    #         # clear message_box every 300 ms
    #         if self.game_timer % 300 == 0:
    #             mb.delete_messages_before(self.game_timer)

    #     self.msg_box.send_message("Over", "game over")

    def get_current_time(self):
        return self.game_timer

    def advance_game_time_by(self, ms):
        self.game_timer += ms

    def is_game_running(self):
        return self.game_running_flag

    def is_game_finished(self):
        return not self.game_running_flag

    def stop_game(self):
        self.game_running_flag = False

    def check_game_end_condition(self):
        state = True

        if self.players_and_dragons_have_spawned_flag:
            gb = self.leadingstate.get_gameboard()

            if gb.get_dragon_count() <= 0 and gb.get_human_count() > 0:
                print "Humans win!"
                state = False
            elif gb.get_dragon_count() > 0 and gb.get_human_count() <= 0:
                print "Dragons win!"
                state = False

        self.game_running_flag = state

    def get_list_of(self, c):
        return self.leadingstate.get_gameboard().get_list_of(c)

    def get_gameboard(self):
        return self.leadingstate.get_gameboard()

    def get_gamestate(self):
        return self.leadingstate

    def process_action(self, action):
        # action is a dictionary
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
            obj_name = action["player_id"]
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

            # precondition for game end condition check
            if not self.players_and_dragons_have_spawned_flag and self.humans_joined > 0 and self.dragons_joined > 0:
                self.players_and_dragons_have_spawned_flag = True

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
            target_obj_hp = target_obj.get_attacked(obj.get_ap(), obj.get_name())
            
            if target_obj_hp <= 0:
                self.leadingstate.remove_character(target_obj)

        elif action_type == "heal":
            # heal a character
            #server_id = action["#server_id"]

            obj_id = action["obj_id"]
            target_id = action["target_id"]

            obj = self.leadingstate.get_object_by_id(obj_id)
            target_obj = self.leadingstate.get_object_by_id(target_id)
            target_obj.get_healed(obj.get_ap(), obj.get_name())

    def process_action_list(self, action_list):
        for action in action_list:
            self.process_action(self, action)

    def get_message_box(self):
        return self.msg_box

    def get_object(self, x=None, y=None):
        return self.leadingstate.get_object(x,y)

    def get_width(self):
        return self.width

    def get_height(self):
        return self.height

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
