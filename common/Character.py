from random import randint

class Character(object):
    def __init__(self, obj_id, name, hp, max_hp, ap, x, y, char_type, verbose=True):
        self.obj_id = obj_id
        self.name = name
        self.max_hp = max_hp
        self.x = x
        self.y = y
        self.hp = hp
        self.ap = ap
        self.type = char_type
        self.verbose = verbose

    def __str__(self):
        return "char:(%s, %s, loc(%d,%d), hp:%d, ap:%d) " % (self.type,
            self.obj_id, self.x, self.y, self.hp, self.ap)

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

    def set_hp(self, hp):
        self.hp = hp

    def set_x(self, x):
        self.x = x

    def set_y(self, y):
        self.y = y

class Human(Character):
    def __init__(self, obj_id, name, hp, max_hp, ap, x, y, verbose=True):
        Character.__init__(self, obj_id, name, hp, max_hp, ap, x, y, char_type='h', verbose=verbose)

        self.hp = hp
        self.max_hp = self.hp
        self.ap = ap

        self.type = 'h'
        if self.verbose: print "new player %s (%d, %d) spawns.." % (self.name, self.x, self.y)
        if self.verbose: print "..hp %d/%d" % (self.hp, self.max_hp)
        if self.verbose: print "..ap %d" % self.ap

class Dragon(Character):
    def __init__(self, obj_id, name, hp, max_hp, ap, x, y, verbose=True):
        Character.__init__(self, obj_id, name, hp, max_hp, ap, x, y, char_type='d', verbose=verbose)

        self.hp = hp
        self.max_hp = self.hp
        self.ap = ap

        self.type = 'd'
        if self.verbose: print "new dragon %s (%d, %d) spawns.." % (self.name, self.x, self.y)
        if self.verbose: print "..hp %d/%d" % (self.hp, self.max_hp)
        if self.verbose: print "..ap %d" % self.ap
