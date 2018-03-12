from random import randint

class Character(object):
    def __init__(self, obj_id, name, gameboard, hp, ap, x, y, char_type, verbose=True):
        self.obj_id = obj_id
        self.name = name
        self.max_hp = hp
        self.x = x
        self.y = y
        self.hp = hp
        self.ap = ap
        self.gameboard = gameboard
        self.type = char_type
        self.verbose = verbose
        
        self.gameboard.set_object(self, self.x, self.y)

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

    def is_alive(self):
        return self.hp > 0

    def get_attacked(self, ap, attacker_name):
        if self.verbose: print "%s (%d, %d) is attacked by %s (%d damage)" % (self.name, self.x, self.y, attacker_name, ap)
        self.hp -= ap
        if self.verbose: print "..%s's hp is now %d/%d" % (self.name, self.hp, self.max_hp)
        if self.hp <= 0:
            if self.verbose: print "..%s (%d, %d) is slained!" % (self.name, self.x, self.y)
            self.gameboard.del_object(self.type, self.x, self.y)
        return self.hp

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
