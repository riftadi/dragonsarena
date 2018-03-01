#!/usr/bin/python
import time
import pygame
from random import randint
from threading import Thread
import sys

# Modeller classes
class UnifiedMessageBox(object):
    def __init__(self):
        self.message_box = []
        self.server_id = 1
        self.msg_counter = 1

    def get_list_len(self):
        return len(self.message_box)

    def delete_messages_before(self, time):
        new_msg_list = []
        for msg in self.message_box:
            if msg["timestamp"] >= time:
                new_msg_list.append(msg)
        self.message_box = new_msg_list

    def get_all_messages(self):
        return self.message_box

    def get_messages(self, time_from, time_until):
        result_list = []
        for msg in self.message_box:
            if msg["timestamp"] >= time_from and msg["timestamp"] < time_until:
                result_list.append(msg)

        return result_list

    def put_message(self, input_dict):
        # input sample: {"msg_id" : 1001, "global_id" : 1001, "timestamp": 359}
        input_dict["msg_id"] = self.server_id * 10000 + self.msg_counter
        self.msg_counter += 1
        self.message_box.append(input_dict)

class GameState(object):
    """
        Container class for characters and gameboard
    """
    def __init__(self, width, height):
        self.gb = GameBoard(width, height)
        self.character_list = []
        self.action_list = []

        # action_dict = {10001 : {'action_type' : 'spawn', 'msg_id' : 10001, ...},
        #                10002 : {'action_type' : 'move', 'msg_id' : 10002, ...},}

    def get_characters(self):
        return self.character_list

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

            # clear message_box every 300 ms
            if self.game_timer % 300 == 0:
                mb.delete_messages_before(self.game_timer)

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
            server_id = action["server_id"]
            obj_id = action["obj_id"]

            # now do the action
            if action_type == "spawn":
                # create a new character
                obj_name = action["obj_name"]
                obj_type = action["obj_type"]

                # x = action["x"]
                # y = action["y"]
                # hp = action["hp"]
                # ap = action["ap"]

                new_obj = None
                if obj_type == 'h':
                    new_obj = Human(obj_id, obj_name, self.leadingstate.get_gameboard(), verbose=self.verbose)
                elif obj_type == 'd':
                    new_obj = Dragon(obj_id, obj_name, self.leadingstate.get_gameboard(), verbose=self.verbose)

                self.leadingstate.add_character(new_obj)

            elif action_type == "move":
                # move a character
                server_id = action["server_id"]

                obj_id = action["obj_id"]

                x = action["x"]
                y = action["y"]

                obj = self.leadingstate.get_object_by_id(obj_id)
                obj.move_to(x,y)

            elif action_type == "attack":
                # attack a character
                server_id = action["server_id"]

                obj_id = action["obj_id"]
                target_id = action["target_id"]

                obj = self.leadingstate.get_object_by_id(obj_id)
                target_obj = self.leadingstate.get_object_by_id(target_id)
                target_obj.get_attacked(obj.get_ap(), obj.get_name())

            elif action_type == "heal":
                # heal a character
                server_id = action["server_id"]

                obj_id = action["obj_id"]
                target_id = action["target_id"]

                obj = self.leadingstate.get_object_by_id(obj_id)
                target_obj = self.leadingstate.get_object_by_id(target_id)
                target_obj.get_healed(obj.get_ap(), obj.get_name())

    def get_current_time(self):
        return self.game_timer

    def get_message_box(self):
        return self.msg_box

    def get_object(self, x, y):
        return self.leadingstate.get_object(x,y)

    def get_width(self):
        return self.width

    def get_height(self):
        return self.height

    def get_current_time(self):
        return self.game_timer

    def is_game_running(self):
        return self.game_running_flag

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
        if gb.get_dragon_count() <= 0 and gb.get_human_count() > 0:
            print "humans win!"
            self.stop_game()
            return True
        elif gb.get_dragon_count() > 0 and gb.get_human_count() <= 0:
            print "dragons win!"
            self.stop_game()
            return True

        return False

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

    def get_object(self, x, y):
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

class Character(object):
    def __init__(self, obj_id, name, gameboard, hp, ap, x, y, char_type, verbose=True):
        self.obj_id = obj_id
        self.name = name
        self.max_hp = hp
        self.hp = hp
        self.ap = ap
        self.gameboard = gameboard
        self.type = char_type
        self.random_delay = randint(300,1000)
        self.verbose = verbose

        if x == -1 or y == -1:
            safely_placed = False

            while not safely_placed:
                prop_x = randint(0, self.gameboard.get_width()-1)
                prop_y = randint(0, self.gameboard.get_height()-1)

                if self.gameboard.get_object(prop_x, prop_y) == None:
                    safely_placed = True
                    self.x = prop_x
                    self.y = prop_y
                    self.gameboard.set_object(self, prop_x, prop_y)
        else:
            self.x = x
            self.y = y

    def get_obj_id(self):
        return self.obj_id

    def get_name(self):
        return self.name

    def get_hp(self):
        return self.hp

    def get_max_hp(self):
        return self.max_hp

    def get_ap(self):
        return self.ap

    def get_x(self):
        return self.x

    def get_y(self):
        return self.y

    def get_type(self):
        return self.type

    def get_random_delay(self):
        return self.random_delay

    def is_alive(self):
        return self.hp > 0

    def get_attacked(self, ap, attacker_name):
        if self.verbose: print "%s (%d, %d) is attacked by %s (%d damage)" % (self.name, self.x, self.y, attacker_name, ap)
        self.hp -= ap
        if self.verbose: print "..%s's hp is now %d/%d" % (self.name, self.hp, self.max_hp)
        if self.hp <= 0:
            if self.verbose: print "..%s (%d, %d) is slained!" % (self.name, self.x, self.y)
            self.gameboard.del_object(self.type, self.x, self.y)

class Human(Character):
    def __init__(self, obj_id, name, gameboard, hp=-1, ap=-1, x=-1, y=-1, verbose=True):
        Character.__init__(self, obj_id, name, gameboard, hp, ap, x, y, char_type='h', verbose=verbose)

        if hp == -1:
            self.hp = randint(11,20)
        else:
            self.hp = hp

        self.max_hp = self.hp

        if ap == -1:
            self.ap = randint(1,10)
        else:
            self.ap = ap

        self.type = 'h'
        if self.verbose: print "new player %s (%d, %d) spawns.." % (self.name, self.x, self.y)
        if self.verbose: print "..hp %d/%d" % (self.hp, self.max_hp)
        if self.verbose: print "..ap %d" % self.ap

    def get_healed(self, ap, healer_name):
        if self.verbose: print "%s (%d, %d) is healed by %s" % (self.name, self.x, self.y, healer_name)

        if self.hp + ap > self.max_hp:
            self.hp = self.max_hp
        else:
            self.hp += ap

        if self.verbose: print "..%s's hp is now %d/%d" % (self.name, self.hp, self.max_hp)

    def move_to(self, new_x, new_y):
        if (abs(self.x - new_x) + abs(self.y - new_y)) == 1:
            # check whether it only moves one step
            obj = self.gameboard.get_object(new_x, new_y)
            if obj == None:
                # check whether there is another object on the new coordinate
                self.gameboard.move_object(self.x, self.y, new_x, new_y)
                self.x = new_x
                self.y = new_y
            else:
                if self.verbose: print "..blocked by %s (%d, %d)" % (obj.get_name(), obj.get_x(),obj.get_y())

class Dragon(Character):
    def __init__(self, obj_id, name, gameboard, hp=-1, ap=-1, x=-1, y=-1, verbose=True):
        Character.__init__(self, obj_id, name, gameboard, hp, ap, x, y, char_type='d', verbose=verbose)

        if hp == -1:
            self.hp = randint(50,100)
        else:
            self.hp = hp

        self.max_hp = self.hp

        if ap == -1:
            self.ap = randint(5,20)
        else:
            self.ap = ap

        self.type = 'd'
        if self.verbose: print "new dragon %s (%d, %d) spawns.." % (self.name, self.x, self.y)
        if self.verbose: print "..hp %d/%d" % (self.hp, self.max_hp)
        if self.verbose: print "..ap %d" % self.ap

#################################################################
# Viewer classes

#################################################################
# Controller classes
class Bot(Thread):
    def __init__(self, obj_id, gamestate, msg_box, verbose):
        Thread.__init__(self)
        self.obj_id = obj_id
        self.obj = None
        self.gamestate = gamestate
        self.verbose = verbose
        self.msg_box = msg_box

        while self.obj == None:
            self.obj = self.gamestate.get_object_by_id(self.obj_id)
            if self.obj != None:
                self.random_delay = self.obj.get_random_delay()

    def do_best_action(self):
        pass

    def run(self):
        while self.obj.is_alive() and self.gamestate.is_game_running():
            self.do_best_action()
            pygame.time.wait(self.random_delay)

    def calculate_distance(self, target_x, target_y):
        # cityblock distance
        return abs(self.obj.get_x() - target_x) + abs(self.obj.get_y() - target_y)

    def heal_target(self, target_obj):
        # target = self.gamestate.get_object(target_x, target_y)
        # if target.get_attacked(self.obj.get_ap(), self.obj.get_name()) <= 0:
        #     # the target dies!
        #     pass
        msg = {"timestamp" : self.gamestate.get_current_time(), "type" : "heal", "obj_id" : self.obj.get_obj_id(),
                 "server_id" : 10000, "target_id" : target_obj.get_obj_id(), "ap" : self.obj.get_ap()}
        self.msg_box.put_message(msg)

    def attack_target(self, target_obj):
        # target = self.gamestate.get_object(target_x, target_y)
        # if target.get_attacked(self.obj.get_ap(), self.obj.get_name()) <= 0:
        #     # the target dies!
        #     pass
        msg = {"timestamp" : self.gamestate.get_current_time(), "type" : "attack", "obj_id" : self.obj.get_obj_id(),
                "server_id" : 10000, "target_id" : target_obj.get_obj_id(), "ap" : self.obj.get_ap()}
        self.msg_box.put_message(msg)

class HumanBot(Bot):
    def __init__(self, obj, gamestate, msg_box, verbose=True):
        Bot.__init__(self, obj, gamestate, msg_box, verbose)
        self.target_x = -1
        self.target_y = -1

    def do_best_action(self):
        if self.obj.is_alive():
            if self.verbose: print "\n%s's (%d, %d) turn" % (self.obj.get_name(), self.obj.get_x(), self.obj.get_y())
            is_dragon_exist, self.target_x, self.target_y = self.find_nearest_dragon()

            if is_dragon_exist:
                try:
                    # try to find friend to heal first
                    is_nearby_friend_need_healing, friend_x, friend_y = self.find_nearest_friend_in_need()

                    if is_nearby_friend_need_healing:
                        friend = self.gamestate.get_object(friend_x, friend_y)
                        friend_name = friend.get_name()
                        friend_x = friend.get_x()
                        friend_y = friend.get_y()
                        if self.verbose: print "..our friend %s (%d, %d) is dying, healing him" % (friend_name, friend_x, friend_y)
                        self.heal_target(friend)
                    else:
                        # try to find some dragon
                        dragon = self.gamestate.get_object(self.target_x, self.target_y)
                        dragon_name = dragon.get_name()
                        dragon_x = dragon.get_x()
                        dragon_y = dragon.get_y()

                        if self.calculate_distance(self.target_x, self.target_y) <= 2:
                            # a dragon is in sight
                            if self.verbose: print "..dragon %s (%d, %d) is in attack range, attacking!" % (dragon_name, dragon_x, dragon_y)
                            self.attack_target(dragon)
                        else:
                            # no dragon in sight
                            new_x, new_y = self.get_next_step(self.target_x, self.target_y)
                            if self.verbose: print "..see dragon %s (%d, %d), approaching via (%d, %d)" % (dragon_name, dragon_x, dragon_y, new_x, new_y)
                            self.move_to(new_x, new_y)

                except:
                    pass

    def move_to(self, new_x, new_y):
        msg = {"timestamp" : self.gamestate.get_current_time(), "type" : "move", "obj_id" : self.obj.get_obj_id(),
                 "server_id" : 10000, "x" : new_x, "y" : new_y}
        self.msg_box.put_message(msg)

    def find_nearest_dragon(self):
        nearest_dist = 99999
        nearest_target_x = 99999
        nearest_target_y = 99999
        is_dragon_exist = False

        dragon_list = self.gamestate.get_gameboard().get_list_of('d')

        for dragon in dragon_list:
            dr_x = dragon.get_x()
            dr_y = dragon.get_y()
            dist = self.calculate_distance(dr_x, dr_y)
            if dist < nearest_dist:
                nearest_dist = dist
                nearest_target_x = dr_x
                nearest_target_y = dr_y
                is_dragon_exist = True

        return is_dragon_exist, nearest_target_x, nearest_target_y

    def find_nearest_friend_in_need(self):
        nearest_friend_x = 99999
        nearest_friend_y = 99999
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
                    nearest_friend_x = hum_x
                    nearest_friend_y = hum_y
                    is_nearby_friend_need_healing = True
                    break
            except:
                break

        return is_nearby_friend_need_healing, nearest_friend_x, nearest_friend_y

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
            # prioritze y-axis otherwise
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
    def __init__(self, obj, gamestate, msg_box, verbose=True):
        Bot.__init__(self, obj, gamestate, msg_box, verbose)

    def do_best_action(self):
        if self.obj.is_alive():
            if self.verbose: print "\n%s's (%d, %d) turn" % (self.obj.get_name(), self.obj.get_x(), self.obj.get_y())
            is_human_exist, target_x, target_y = self.find_nearest_human()
            if is_human_exist:
                try:
                    prey = self.gamestate.get_object(target_x, target_y)
                    if self.verbose: print "..player %s (%d, %d) is in attack range, attacking!" % (prey.get_name(), prey.get_x(), prey.get_y())
                    self.attack_target(prey)
                except:
                    pass

    def find_nearest_human(self):
        nearest_target_x = 99999
        nearest_target_y = 99999
        is_human_exist = False

        human_list = self.gamestate.get_gameboard().get_list_of('h')

        for human in human_list:
            hum_x = human.get_x()
            hum_y = human.get_y()
            if self.calculate_distance(hum_x, hum_y) <= 2:
                nearest_target_x = hum_x
                nearest_target_y = hum_y
                is_human_exist = True
                break

        return is_human_exist, nearest_target_x, nearest_target_y

class GUIDisplay(object):
    """
        Viewer class
    """
    def __init__(self, nhuman, ndragon, sleep_time=100, verbose=True):
        counter = 0
        self.msg_box = UnifiedMessageBox()
        self.M = TSSEngine(25, 25, self.msg_box, verbose=verbose)
        self.timer = 0

        self.M.setName('gs_thread')
        self.M.start()

        self.pl_id = 0
        self.server_id = 10000

####
        # Define some colors
        BLACK = (0, 0, 0)
        WHITE = (255, 255, 255)
        GREEN = (0, 255, 0)
        RED = (255, 0, 0)
         
        # This sets the WIDTH and HEIGHT of each grid location
        WIDTH = 20
        HEIGHT = 20
         
        # This sets the margin between each cell
        MARGIN = 2

        QUIT = False
        pygame.init()

        # Set the HEIGHT and WIDTH of the screen
        WINDOW_SIZE = [552, 552]
        screen = pygame.display.set_mode(WINDOW_SIZE)

        # Set title of screen
        pygame.display.set_caption("Dragon's Arena")

        im_human = pygame.image.load("human.bmp")
        im_dragon = pygame.image.load("dragon.bmp")

####
        self.plist = []
        for i in xrange(nhuman):
            # p = Human("p%d" % (i+1), self.M, verbose=verbose)
            msg = {"timestamp" : self.M.get_current_time(), "type" : "spawn", "server_id" : self.server_id,
                     "obj_name" : "p%d"%(self.pl_id+1), "obj_id" : self.server_id+self.pl_id, "obj_type" : "h"}
            self.msg_box.put_message(msg)
            self.plist.append(self.server_id+self.pl_id)
            self.pl_id += 1
        for i in xrange(ndragon):
            # d = Dragon("d%d" % (i+1), self.M, verbose=verbose)
            msg = {"timestamp" : self.M.get_current_time(), "type" : "spawn", "server_id" : self.server_id,
                     "obj_name" : "d%d"%(self.pl_id+1), "obj_id" : self.server_id+self.pl_id, "obj_type" : "d"}
            self.msg_box.put_message(msg)
            self.plist.append(self.server_id+self.pl_id)
            self.pl_id += 1

        # wait a few moment for the TSSengine to create the characters
        print "initializing bots.."
        pygame.time.wait(100)

        self.blist = []
        for i in xrange(nhuman):
            hb = HumanBot(self.plist[i], self.M, self.msg_box, verbose=verbose)
            self.blist.append(hb)
            hb.setName('bot%d_thread' % i)
            hb.start()

        for i in xrange(ndragon):
            db = DragonBot(self.plist[nhuman+i], self.M, self.msg_box, verbose=verbose)
            self.blist.append(db)
            hb.setName('bot%d_thread' % (nhuman + i))
            db.start()

        while not self.M.is_game_finished() and not QUIT:
            for event in pygame.event.get():  # User did something
                if event.type == pygame.QUIT:  # If user clicked close
                    QUIT = True
            screen.fill(BLACK)
         
            # Draw the grid
            for row in xrange(25):
                for column in xrange(25):
                    pygame.draw.rect(screen,
                                     WHITE,
                                     [(MARGIN + HEIGHT) * row + MARGIN,
                                      (MARGIN + WIDTH) * column + MARGIN,
                                      HEIGHT,
                                      WIDTH])
                    obj = self.M.get_object(row, column)
                    if obj != None:
                        if obj.get_type() == 'h':
                            screen.blit(im_human, ((MARGIN + HEIGHT) * row + MARGIN,
                                              (MARGIN + WIDTH) * column + MARGIN))
                        elif obj.get_type() == 'd':
                            screen.blit(im_dragon, ((MARGIN + HEIGHT) * row + MARGIN,
                                              (MARGIN + WIDTH) * column + MARGIN))
         
            # Go ahead and update the screen with what we've drawn.
            pygame.display.flip()
            pygame.time.wait(sleep_time)

            counter += 1

        # game is finished, stop threads
        self.M.stop_game()

        self.M.join()
        for bot in self.blist:
            bot.join()

        pygame.quit()

#################################################################
if __name__ == '__main__':
    print "starting dragons arena.."
    if len(sys.argv) == 3:
        human_count = int(sys.argv[1])
        dragon_count = int(sys.argv[2])
    else:
        human_count = 100
        dragon_count = 20

    GUIDisplay(human_count, dragon_count, 100, False)
    print "game end.."
