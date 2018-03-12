from random import randint
from threading import Thread
import pygame

from GameState import GameState

import time


MIN_DELAY = 300
MAX_DELAY = 800

class Bot(Thread):
    def __init__(self, obj_id, msg_box, verbose):
        Thread.__init__(self)
        self.obj_id = obj_id
        self.gamestate = GameState() 
        self.verbose = verbose
        self.msg_box = msg_box
        self.obj = None
        self.seen_dragons = 0
        self.seen_humans = 0
        self.done = False

        self.random_delay = randint(MIN_DELAY,MAX_DELAY)


    def do_best_action(self):
        pass

    def is_done(self):
        if self.done == True:
            print ("Done")
        return self.done

    def update_gamestate(self, gamestate):
        gb = gamestate.get_gameboard()
        if gb.get_human_count() > self.seen_humans:
            self.seen_humans = gb.get_human_count()
        if gb.get_dragon_count() > self.seen_dragons:
            self.seen_dragons = gb.get_dragon_count()

        self.gamestate = gamestate

    def run(self):
        #wait till character object is set
        while self.obj == None:
            self.obj = self.gamestate.get_object_by_id(self.obj_id)
        #run bot actions
        while self.obj.is_alive() and self.game_still_running():
            # update obj
            self.obj = self.gamestate.get_object_by_id(self.obj_id)
            if self.obj is not None:
                self.do_best_action()
            pygame.time.wait(self.random_delay)

        self.done = True
    
    def game_still_running(self):
        gb = self.gamestate.get_gameboard()
        if self.seen_dragons < 1 or self.seen_humans < 1:
            return True

        if gb.get_dragon_count() <= 0 and gb.get_human_count() > 0:
            print "humans win!"
            return False
        elif gb.get_dragon_count() > 0 and gb.get_human_count() <= 0:
            print "dragons win!"
            return False

        return True

    def calculate_distance(self, target_x, target_y):
        # cityblock distance
        return abs(self.obj.get_x() - target_x) + abs(self.obj.get_y() - target_y)

    def heal_target(self, target_obj):
        msg = {
            "type" : "heal",
            "player_id" : self.obj.get_obj_id(),
            "target_id" : target_obj.get_obj_id(),
        }
        self.msg_box.send_message(msg)

    def attack_target(self, target_obj):
        msg = {
            "type" : "attack",
            "player_id" : self.obj.get_obj_id(),
            "target_id" : target_obj.get_obj_id(),
        }
        self.msg_box.send_message(msg)

class HumanBot(Bot):
    def __init__(self, obj_id, msg_box, verbose=True):
        Bot.__init__(self, obj_id, msg_box, verbose)

    def do_best_action(self):
        if self.obj is None:
            return
        if self.obj.is_alive():     
            if self.verbose: print "\n%s's (%d, %d) turn" % (self.obj.get_name(), self.obj.get_x(), self.obj.get_y())
            is_dragon_exist, dragon = self.find_nearest_dragon()

            if is_dragon_exist:
                # try to find friend to heal first
                is_nearby_friend_need_healing, friend = self.find_nearest_friend_in_need()

                if is_nearby_friend_need_healing:
                    if self.verbose: print "..our friend %s (%d, %d) is dying, healing him" % \
                            (friend.get_name(), friend.get_x(), friend.get_y())
                    self.heal_target(friend)
                else:
                    # try to find some dragon
                    if self.calculate_distance(dragon.get_x(), dragon.get_y()) <= 2:
                        # a dragon is in sight
                        if self.verbose: print "..dragon %s (%d, %d) is in attack range, attacking!" % \
                                (dragon.get_name(), dragon.get_x(), dragon.get_y())
                        self.attack_target(dragon)
                    else:
                        # no dragon in sight
                        new_x, new_y = self.get_next_step(dragon.get_x(), dragon.get_y())
                        if self.verbose: print "..see dragon %s (%d, %d), approaching via (%d, %d)" % \
                                (dragon.get_name(), dragon.get_x(), dragon.get_y(), new_x, new_y)
                        self.move_to(new_x, new_y)

    def move_to(self, new_x, new_y):
        msg = {
            "type" : "move",
            "player_id" : self.obj.get_obj_id(),
            "x" : new_x,
            "y" : new_y
        }
        self.msg_box.send_message(msg)

    def find_nearest_dragon(self):
        nearest_dist = 99999
        nearest_target = None
        is_dragon_exist = False

        dragon_list = self.gamestate.get_gameboard().get_list_of('d')

        for dragon in dragon_list:
            dragon_x = dragon.get_x()
            dragon_y = dragon.get_y()
            dist = self.calculate_distance(dragon_x, dragon_y)

            if dist < nearest_dist:
                nearest_dist = dist
                nearest_target = dragon
                is_dragon_exist = True

        return is_dragon_exist, nearest_target

    def find_nearest_friend_in_need(self):
        nearest_friend = None
        is_nearby_friend_need_healing = False

        human_list = self.gamestate.get_gameboard().get_list_of('h')

        for human in human_list:
            hum_x = human.get_x()
            hum_y = human.get_y()

            if hum_x == self.obj.get_x() and hum_y == self.obj.get_y():
                # it is us, pass
                continue
            try:
                dist = self.calculate_distance(hum_x, hum_y)
                hum_obj = self.gamestate.get_object(hum_x, hum_y)
                hum_hp_ratio = hum_obj.get_hp() / hum_obj.get_max_hp()

                if hum_hp_ratio <= 0.5 and dist <= 5:
                    nearest_friend = hum_obj
                    is_nearby_friend_need_healing = True
                    break
            except:
                break

        return is_nearby_friend_need_healing, nearest_friend

    def get_next_step(self, target_x, target_y):
        x = self.obj.get_x()
        y = self.obj.get_y()

        chance = randint(0, 1)

        if chance == 0:
            # 50:50 chance prioritize x-axis
            if x < target_x:
                # move one right
                x += 1
            elif x > target_x:
                # move one left
                x -= 1
            else:
                # we are in the same x as the target
                if y < target_y:
                    # move one up
                    y += 1
                elif y > target_y:
                    # move one down
                    y -= 1
        else:
            # prioritize y-axis otherwise
            if y < target_y:
                # move one up
                y += 1
            elif y > target_y:
                # move one down
                y -= 1
            else:
                # we are in the same y as the target
                if x < target_x:
                    # move one right
                    x += 1
                elif x > target_x:
                    # move one left
                    x -= 1

        return x, y

class DragonBot(Bot):
    def __init__(self, obj_id, msg_box, verbose=True):
        Bot.__init__(self, obj_id, msg_box, verbose)

    def do_best_action(self):
        if self.obj is None:
            return
        if self.obj.is_alive():
            if self.verbose: print "\n%s's (%d, %d) turn" % (self.obj.get_name(), self.obj.get_x(), self.obj.get_y())
            is_prey_exist, prey = self.find_nearest_human()
            if is_prey_exist:
                try:
                    if self.verbose: print "..player %s (%d, %d) is in attack range, attacking!" % \
                        (prey.get_name(), prey.get_x(), prey.get_y())
                    self.attack_target(prey)
                except:
                    pass

    def find_nearest_human(self):
        nearest_target = None
        is_human_exist = False

        human_list = self.gamestate.get_gameboard().get_list_of('h')

        for human in human_list:
            hum_x = human.get_x()
            hum_y = human.get_y()

            if self.calculate_distance(hum_x, hum_y) <= 2:
                nearest_target = human
                is_human_exist = True
                break

        return is_human_exist, nearest_target