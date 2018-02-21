#!/usr/bin/python
import time
import pygame
from random import randint

# Modeller classes
class GameBoard(object):
    """
        The board of the game, default size is 25x25
    """

    def __init__(self, width=25, height=25):
        self.width = width
        self.height = height
        self.gameboard = []

        for i in xrange(width):
            self.gameboard.append([])
            for j in xrange(height):
                self.gameboard[i].append(None)

    def set_object(self, obj, x, y):
        self.gameboard[x][y] = obj

    def get_object(self, x, y):
        return self.gameboard[x][y]

    def get_width(self):
        return self.width

    def get_height(self):
        return self.height

    def move_object(self, old_x, old_y, new_x, new_y):
        self.gameboard[new_x][new_y] = self.gameboard[old_x][old_y]
        self.gameboard[old_x][old_y] = None

    def del_object(self, x, y):
        self.gameboard[x][y] = None

    def get_coord_list_of(self, c):
        obj_list = []

        for x in xrange(self.width):
            for y in xrange(self.height):
                obj = self.get_object(x, y)
                if obj != None:
                    if obj.get_type() == c:
                        obj_list.append((x, y))

        return obj_list

class Character(object):
    def __init__(self, name, gameboard, hp, ap, x, y):
        self.name = name
        self.max_hp = hp
        self.hp = hp
        self.ap = ap
        self.gameboard = gameboard
        self.type = 'c'

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

    def is_alive(self):
        return self.hp > 0

    def get_attacked(self, ap, name):
        print "%s (%d, %d) is attacked by %s (%d damage)" % (self.name, self.x, self.y, name, ap)
        self.hp -= ap
        print "..%s's hp is now %d/%d" % (self.name, self.hp, self.max_hp)
        if self.hp <= 0:
            print "..%s (%d, %d) is slained!" % (self.name, self.x, self.y)
            self.gameboard.del_object(self.x, self.y)

class Human(Character):
    def __init__(self, name, gameboard, hp=-1, ap=-1, x=-1, y=-1):
        Character.__init__(self, name, gameboard, hp, ap, x, y)

        if hp == -1:
            self.hp = randint(10,20)
        else:
            self.hp = hp

        self.max_hp = self.hp

        if ap == -1:
            self.ap = randint(1,10)
        else:
            self.ap = ap

        self.type = 'h'
        self.gameboard.set_object(self, self.x, self.y)
        print "new player %s (%d, %d) spawns.." % (self.name, self.x, self.y)
        print "..hp %d/%d" % (self.hp, self.max_hp)
        print "..ap %d" % self.ap

    def get_healed(self, ap, name):
        print "%s (%d, %d) is healed by %s" % (self.name, self.x, self.y, name)

        if self.hp + ap > self.max_hp:
            self.hp = self.max_hp
        else:
            self.hp += ap

        print "..%s's hp is now %d/%d" % (self.name, self.hp, self.max_hp)

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
                print "..blocked by %s (%d, %d)" % (obj.get_name(), obj.get_x(),obj.get_y())

class Dragon(Character):
    def __init__(self, name, gameboard, hp=-1, ap=-1, x=-1, y=-1):
        Character.__init__(self, name, gameboard, hp, ap, x, y)

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
        self.gameboard.set_object(self, self.x, self.y)
        print "new dragon %s (%d, %d) spawns.." % (self.name, self.x, self.y)
        print "..hp %d/%d" % (self.hp, self.max_hp)
        print "..ap %d" % self.ap

#################################################################
# Viewer classes
class GameBoardViewer(object):
    def __init__(self, gameboard):
        self.app = Tk()
        self.app.title('Dragons Arena')
        self.app.resizable(width=False, height=False)
        self.font = Font(family="Helvetica", size=24)
        self.buttons = {}
        self.board = gameboard

        for x in xrange(self.board.get_width()):
            for y in xrange(self.board.get_height()):
                button = Button(self.app, font=self.font, width=1, height=1)
                button.grid(row=x, column=y)
                self.buttons[x,y] = button
        self.update()
        threading.Thread.__init__(self)

    def run(self):
        self.app.mainloop()

    def update(self):
        for x in xrange(self.board.get_width()):
            for y in xrange(self.board.get_height()):
                obj = self.board.get_object(x,y)
                if obj != None:
                    text = self.board.get_object(x,y).get_name()
                    self.buttons[x,y]['text'] = text
                    # self.buttons[x,y]['disabledforeground'] = 'black'
                else:
                    self.buttons[x,y]['state'] = 'normal'

#################################################################
# Controller classes
class Bot(object):
    def __init__(self, obj, gameboard):
        self.obj = obj
        self.gameboard = gameboard

    def calculate_distance(self, target_x, target_y):
        # cityblock distance
        return abs(self.obj.get_x() - target_x) + abs(self.obj.get_y() - target_y)

    def attack_target(self, target_x, target_y):
        target = self.gameboard.get_object(target_x, target_y)
        if target.get_attacked(self.obj.get_ap(), self.obj.get_name()) <= 0:
            # the target dies!
            pass

class HumanBot(Bot):
    def __init__(self, obj, gameboard):
        Bot.__init__(self, obj, gameboard)
        self.target_x = -1
        self.target_y = -1

    def do_best_action(self):
        print "\n%s's (%d, %d) turn" % (self.obj.get_name(), self.obj.get_x(), self.obj.get_y())
        is_dragon_exist, self.target_x, self.target_y = self.find_nearest_dragon()

        if is_dragon_exist:
            dragon = self.gameboard.get_object(self.target_x, self.target_y)

            if self.calculate_distance(self.target_x, self.target_y) <= 2:
                print "..dragon %s (%d, %d) is in attack range, attacking!" % (dragon.get_name(), dragon.get_x(), dragon.get_y())
                self.attack_target(self.target_x, self.target_y)
            else:
                is_nearby_friend_need_healing, friend_x, friend_y = self.find_nearest_friend_in_need()

                if is_nearby_friend_need_healing:
                    friend = self.gameboard.get_object(friend_x, friend_y)
                    print "..our friend %s (%d, %d) is dying, healing him" % (friend.get_name(), friend.get_x(), friend.get_y())
                    friend.get_healed(self.obj.get_ap(), self.obj.get_name())
                else:
                    new_x, new_y = self.get_next_step(self.target_x, self.target_y)
                    print "..see dragon %s (%d, %d), approaching via (%d, %d)" % (dragon.get_name(), dragon.get_x(), dragon.get_y(), new_x, new_y)
                    self.obj.move_to(new_x, new_y)
        else:
            # no more dragons, we have won!
            pass

    def find_nearest_dragon(self):
        nearest_dist = 99999
        nearest_target_x = 99999
        nearest_target_y = 99999
        is_dragon_exist = False

        dragon_list = self.gameboard.get_coord_list_of('d')

        for dragon in dragon_list:
            dr_x, dr_y = dragon
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

        human_list = self.gameboard.get_coord_list_of('h')

        for human in human_list:
            hum_x, hum_y = human
            if hum_x == self.obj.get_x() and hum_y == self.obj.get_y():
                # it is us, pass
                continue

            dist = self.calculate_distance(hum_x, hum_y)
            hum_obj = self.gameboard.get_object(hum_x, hum_y)
            hum_hp_ratio = hum_obj.get_hp() / hum_obj.get_max_hp()

            if hum_hp_ratio <= 0.5 and dist <= 5:
                nearest_friend_x = hum_x
                nearest_friend_y = hum_y
                is_nearby_friend_need_healing = True
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
    def __init__(self, obj, gameboard):
        Bot.__init__(self, obj, gameboard)

    def do_best_action(self):
        print "\n%s's (%d, %d) turn" % (self.obj.get_name(), self.obj.get_x(), self.obj.get_y())
        is_human_exist, target_x, target_y = self.find_nearest_human()
        if is_human_exist:
            prey = self.gameboard.get_object(target_x, target_y)
            print "..player %s (%d, %d) is in attack range, attacking!" % (prey.get_name(), prey.get_x(), prey.get_y())
            self.attack_target(target_x, target_y)
        # else:
        # no more humans, dragons have won!

    def find_nearest_human(self):
        nearest_target_x = 99999
        nearest_target_y = 99999
        is_human_exist = False
        human_list = self.gameboard.get_coord_list_of('h')

        for human in human_list:
            hmn_x, hmn_y = human
            if self.calculate_distance(hmn_x, hmn_y) <= 2:
                nearest_target_x = hmn_x
                nearest_target_y = hmn_y
                is_human_exist = True

        return is_human_exist, nearest_target_x, nearest_target_y

class Game(object):
    """
        Main controller class
    """
    def __init__(self, nhuman, ndragon, sleep_time=200):
        counter = 0
        self.M = GameBoard(25, 25)

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
            p = Human("p%d" % (i+1), self.M)
            self.plist.append(p)
        for i in xrange(ndragon):
            d = Dragon("d%d" % (i+1), self.M)
            self.plist.append(d)

        self.blist = []
        for i in xrange(nhuman):
            hb = HumanBot(self.plist[i], self.M)
            self.blist.append(hb)
        for i in xrange(ndragon):
            db = DragonBot(self.plist[nhuman+i], self.M)
            self.blist.append(db)

        while not self.is_game_finished() and not QUIT:
            for event in pygame.event.get():  # User did something
                if event.type == pygame.QUIT:  # If user clicked close
                    QUIT = True

            if self.plist[counter%(nhuman+ndragon)].is_alive():
                self.blist[counter%(nhuman+ndragon)].do_best_action()

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

        pygame.quit()

    def is_game_finished(self):
        dragon_count = 0
        human_count = 0

        for pl in self.plist:
            if pl.is_alive():
                pl_type = pl.get_type()
                if pl_type == 'h':
                    # it's human
                    human_count += 1
                elif pl_type == 'd':
                    # it's dragon
                    dragon_count += 1

        if dragon_count == 0 and human_count > 0:
            print "humans win!"
            return True
        elif dragon_count > 0 and human_count == 0:
            print "dragons win!"
            return True

        return False

#################################################################
if __name__ == '__main__':
    print "starting dragons arena.."
    Game(100, 20, 50)
    print "game end.."
