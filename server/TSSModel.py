from threading import Thread
import pygame
import json

from common.GameState import GameState
from common.Character import *

### --TODO-- THIS CLASS IS NOT WORKER CLASS, SO NO THREAD BELONG HERE
class TSSModel(object):
    def __init__(self, width, height, start_time, verbose=True):
        self.width = width
        self.height = height
        self.start_time = start_time
        self.verbose = verbose

        self.leadingstate = GameState(self.width, self.height, self.verbose)
        # --TODO-- add more trailing state
        # self.trailingstate01board = GameState(self.width, self.height, self.verbose)
        # self.trailingstate02board = GameState(self.width, self.height, self.verbose)

        # THE ABSOLUTE SOURCE OF TRUTH OF GAME RUNNING STATE
        # It should be True if running, False if not running
        self.game_running_flag = True

        # game timer in milliseconds
        self.game_timer = 0
        self.last_msg_box_access_time = 0
        self.trailing_timer1 = -100

        self.players_and_dragons_have_spawned_flag = False

    def get_current_time(self):
        return self.game_timer

    def get_epoch_time(self):
        return self.start_time

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
            gs = self.leadingstate

            if gs.get_dragon_count() <= 0 and gs.get_human_count() > 0:
                print "Humans win!"
                state = False
            elif gs.get_dragon_count() > 0 and gs.get_human_count() <= 0:
                print "Dragons win!"
                state = False

        self.game_running_flag = state

    def get_list_of(self, c):
        return self.leadingstate.get_list_of(c)

    def get_gamestate(self):
        return self.leadingstate

    def process_action(self, action):
        # action is a dictionary
        # save it for checking purpose in the trailing states
        self.leadingstate.add_action(action)

        # based on message type, do action
        # msg_id = action["msg_id"]
        timestamp = action["timestamp"]
        action_type = action["type"]
        server_id = action["server_id"]

        # now do the action
        if action_type == "gamestart":
            # get start timer indicator from peer
            self.start_time = action["start_time"]
            # update our local game_timer
            self.game_timer = int(round(time.time() * 1000)) - self.start_time

        elif action_type == "spawn":
            # create a new character
            obj_id = action["player_id"]
            obj_name = action["player_id"]
            obj_type = action["player_type"]

            x = action["x"]
            y = action["y"]

            hp = action["hp"]
            ap = action["ap"]

            new_obj = None
            if obj_type == 'human':
                new_obj = Human(obj_id, obj_name, self.leadingstate.get_gameboard(),
                    hp, ap, x, y, verbose=self.verbose)
            elif obj_type == 'dragon':
                new_obj = Dragon(obj_id, obj_name, self.leadingstate.get_gameboard(),
                    hp, ap, x, y, verbose=self.verbose)

            self.leadingstate.add_character(new_obj)

            # precondition for game end condition check, a player must be in the game once
            if not self.players_and_dragons_have_spawned_flag:
                if self.leadingstate.get_human_count() > 0 and self.leadingstate.get_dragon_count() > 0:
                    self.players_and_dragons_have_spawned_flag = True

        elif action_type == "move":
            # move a character
            #server_id = action["#server_id"]

            obj_id = action["player_id"]

            x = action["x"]
            y = action["y"]

            obj = self.leadingstate.move(obj_id, x, y)

        elif action_type == "attack":
            # attack a character
            #server_id = action["#server_id"]

            obj_id = action["player_id"]
            target_id = action["target_id"]

            self.leadingstate.attack(obj_id, target_id)

            # obj = self.leadingstate.get_object_by_id(obj_id)
            # target_obj = self.leadingstate.get_object_by_id(target_id)
            # target_obj_hp = target_obj.get_attacked(obj.get_ap(), obj.get_name())
            
            # if target_obj_hp <= 0:
            #     self.leadingstate.remove_character(target_obj)

        elif action_type == "heal":
            # heal a character
            #server_id = action["#server_id"]

            obj_id = action["obj_id"]
            target_id = action["target_id"]

            self.leadingstate.heal(obj_id, target_id)

            # obj = self.leadingstate.get_object_by_id(obj_id)
            # target_obj = self.leadingstate.get_object_by_id(target_id)
            # target_obj.get_healed(obj.get_ap(), obj.get_name())

    def process_action_list(self, action_list):
        for action in action_list:
            self.process_action(self, action)

    def get_message_box(self):
        return self.msg_box

    def get_object(self, x, y):
        return self.leadingstate.get_object(x,y)

    def get_width(self):
        return self.width

    def get_height(self):
        return self.height

    def get_object_by_id(self, obj_id):
        gs = self.leadingstate
        return gs.get_object_by_id(obj_id)
