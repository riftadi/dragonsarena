from threading import Thread, Lock
import copy
import pygame
import time
import json

from common.GameState import GameState
from common.Character import *
from common.settings import *

### --TODO-- THIS CLASS IS NOT WORKER CLASS, SO NO THREAD BELONG HERE
class TSSModel(object):
    def __init__(self, width, height, start_time, verbose=True):
        self.width = width
        self.height = height
        self.start_time = start_time
        self.verbose = verbose
        self.lock = Lock()

        self.leadingstate = GameState(self.width, self.height, self.verbose)
        self.trailingstate01 = GameState(self.width, self.height, self.verbose)
        # only used during rollback period
        self.tempstate = None
        self.is_in_rollback = False

        # THE ABSOLUTE SOURCE OF TRUTH OF GAME RUNNING STATE
        # It should be True if running, False if not running
        self.game_running_flag = True

        # game timer in milliseconds
        self.game_timer = 0

        # initialize our lamport clock
        self.event_clock = 0

        # locked cells if in the spawning phase
        self.locked_cells = []
        self.client_last_seen_time = {}

        self.players_and_dragons_have_spawned_flag = False

    def update_client_last_seen_time(self, pl_id):
        self.lock.acquire()
        self.client_last_seen_time[pl_id] = self.game_timer
        self.lock.release()

    def get_client_last_seen_time(self, pl_id):
        # get last seen time of player pl_id
        # return None if it doesn't exist
        return self.client_last_seen_time.get(pl_id)

    def get_unactive_player_ids(self):
        # get players with last seen less than a specified time
        # return empty list it doesn't exist
        boundary_time = self.get_current_time() - SERVERSIDE_CLIENT_TIMEOUT
        result = []
        self.lock.acquire()
        try:
            for key, val in self.client_last_seen_time.iteritems():
                obj = self.get_object_by_id(key)
                # only human can be retrieved
                if obj != None:
                    if obj.get_type() == 'h' and val < boundary_time:
                        result.append(key)
        except RuntimeError as e:
            print e
        finally:
            self.lock.release()
                    
        return result

    def get_offline_player_state_by_id(self, obj_id):
        # get info on offline character, return None if it does not exist
        return self.leadingstate.get_offline_player_state_by_id(obj_id)

    def rollback_state(self, command_list):
        self.is_in_rollback = True
        # print "leading_before: %s" % str(self.leadingstate)
        self.tempstate = copy.deepcopy(self.trailingstate01)
        # print "trailing01_before: %s" % str(self.tempstate)
        self.process_action_list(command_list, state_id=TEMP_STATE)
        self.leadingstate = self.tempstate
        # print "leading_after: %s" % str(self.leadingstate)
        self.is_in_rollback = False

    def get_event_clock(self):
        return self.event_clock

    def increase_event_clock(self):
        self.event_clock += 1

    def lock_cell(self, proposal_msg):
        #self.lock.acquire()
        self.locked_cells.append(proposal_msg)
        #self.lock.release()

    def unlock_cell(self, player_id):
        #self.lock.acquire()
        lst = self.locked_cells
        player_idx = next((index for (index, d) in enumerate(lst) if d["player_id"] == player_id), None)
        if player_idx is not None:
            del lst[player_idx]
        #self.lock.release()

    def collide_with_locked(self,x, y):
        #self.lock.acquire()
        for lock in self.locked_cells:
            if lock["x"] == x and lock["y"] == y:
                return True
        #self.lock.release()

        return False
    
    def get_locked(self, player_id):
        #self.lock.acquire()
        lst = self.locked_cells
        player_idx = next((index for (index, d) in enumerate(lst) if d["player_id"] == player_id), None)
        #self.lock.release()
        return lst[player_idx]

    def set_event_clock(self, new_clock):
        self.event_clock = new_clock

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
        if self.is_in_rollback:
            # we're in rollback, don't end game
            self.game_running_flag = True
            return None

        state = True

        if self.players_and_dragons_have_spawned_flag:
            gs = self.get_leadingstate()

            if gs.get_dragon_count() == 0 and gs.get_human_count() > 0:
                print "Humans win!"
                state = False
            elif gs.get_dragon_count() > 0 and gs.get_human_count() == 0:
                print "Dragons win!"
                state = False

        self.game_running_flag = state

    def get_rollback_status(self):
        return self.is_in_rollback

    def get_list_of(self, c):
        return self.leadingstate.get_list_of(c)

    def get_leadingstate(self):
        return self.leadingstate

    def get_firsttrailingstate(self):
        return self.trailingstate01

    def process_action(self, action, state_id=LEADING_STATE):
        # check which state the action is going to be applied to
        # state_id possible values: leading (0), trailing1 (1)
        state = None

        if state_id == LEADING_STATE:
            state = self.leadingstate
        elif state_id == TRAILING_01_STATE:
            state = self.trailingstate01
        elif state_id == TEMP_STATE:
            state = self.tempstate

        # save action for checking purpose in the trailing states
        state.add_action(action)

        # based on message type, do an action
        action_type = action["type"]

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
            max_hp = action["max_hp"]
            ap = action["ap"]

            new_obj = None
            if obj_type == 'h':
                new_obj = Human(obj_id, obj_name,
                    hp, max_hp, ap, x, y, verbose=self.verbose)
            elif obj_type == 'd':
                new_obj = Dragon(obj_id, obj_name,
                    hp, max_hp, ap, x, y, verbose=self.verbose)

            state.add_character(new_obj)

            # finally unlock the player field
            try:
                self.unlock_cell(obj_id)
            except:
                pass

            # precondition for game end condition check, a player must be in the game once
            if not self.players_and_dragons_have_spawned_flag:
                if state.get_human_count() > 0 and state.get_dragon_count() > 0:
                    self.players_and_dragons_have_spawned_flag = True

        elif action_type == "off":
            # a player is offline
            obj_id = action["player_id"]
            state.make_offline(obj_id)

        elif action_type == "move":
            # move a character
            obj_id = action["player_id"]

            x = action["x"]
            y = action["y"]

            if self.collide_with_locked(x,y) == False:
                obj = state.move(obj_id, x, y)

        elif action_type == "attack":
            # attack a character
            obj_id = action["player_id"]
            target_id = action["target_id"]

            state.attack(obj_id, target_id)

        elif action_type == "heal":
            # heal a character
            obj_id = action["obj_id"]
            target_id = action["target_id"]

            state.heal(obj_id, target_id)

    def process_action_list(self, action_list, state_id=LEADING_STATE):
        for action in action_list:
            self.process_action(action, state_id)

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
