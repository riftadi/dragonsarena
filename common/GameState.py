import copy
from common.GameBoard import GameBoard

class GameState(object):
    """
        Container class for characters and gameboard
    """
    def __init__(self, width=25, height=25, verbose=True):
        self.width = width
        self.height = height

        self.gb = GameBoard(self.width, self.height)
        self.verbose = verbose

        self.human_list = []
        self.dragon_list = []

        # used for TSS state checking
        self.executed_msg_ids = []
        self.offline_player_states = []

    def make_offline(self, obj_id):
        # save a character state in offline_players
        char = self.get_object_by_id(obj_id)
        
        if char != None:
            saved_state = {}

            saved_state["obj_id"] = obj_id
            saved_state["hp"] = char.get_hp()
            saved_state["max_hp"] = char.get_max_hp()
            saved_state["ap"] = char.get_ap()
            saved_state["type"] = char.get_type()
            saved_state["x"] = char.get_x()
            saved_state["y"] = char.get_y()

            self.offline_player_states.append(saved_state)

            self.remove_character(char)

    def get_offline_player_state_by_id(self, obj_id):
        # get info on offline character, return None if it does not exist
        char_state = None
        for pl in self.offline_player_states:
            if pl["obj_id"] == obj_id:
                char_state = pl
                break

        return char_state

    def mark_online(self, obj_id):
        # delete a character state from offline_player_states
        char_state = None
        for pl in self.offline_player_states:
            if pl["obj_id"] == obj_id:
                char_state = pl
                break

        if char_state != None:
            self.offline_player_states.remove(char_state)

    def __str__(self):
        hl = []
        dr = []
        for human in self.human_list:
            hl.append(str(human))
        for dragon in self.dragon_list:
            dr.append(str(dragon))
        return "human list: %s\n" % str(hl) + \
                 "dragon list: %s\n" % str(dr) + \
                 "msg id list: %s\n" % str(self.executed_msg_ids)

    def __deepcopy__(self, memo):
        newone = type(self)()

        # copy the simple attributes
        newone.width = self.width
        newone.height = self.height
        newone.verbose = self.verbose

        # create new human and dragon list
        newone.human_list = []
        for human in self.human_list:
            newone.human_list.append(copy.deepcopy(human))

        newone.dragon_list = []
        for dragon in self.dragon_list:
            newone.dragon_list.append(copy.deepcopy(dragon))

        # create new gameboard
        newone.gb = GameBoard(self.width, self.height)

        # put humans and dragons to new gameboard
        for human in newone.human_list:
            newone.gb.set_object(human, human.get_x(), human.get_y())

        for dragon in newone.dragon_list:
            newone.gb.set_object(dragon, dragon.get_x(), dragon.get_y())

        # copy msg_id
        newone.executed_msg_ids = copy.deepcopy(self.executed_msg_ids)

        # copy offline_player_states
        newone.offline_player_states = copy.deepcopy(self.offline_player_states)

        return newone

    def get_characters(self):
        return (self.human_list + self.dragon_list)

    def get_human_count(self):
        return len(self.human_list)

    def get_dragon_count(self):
        return len(self.dragon_list)

    def get_gameboard(self):
        return self.gb

    def get_actions(self):
        return self.action_list

    def is_action_id_exist(self, msg_id):
        """
            Check if there is an action with a specific msg_id, give True is found
        """
        return msg_id in self.executed_msg_ids

    def get_executed_msg_ids(self):
        return self.executed_msg_ids

    def get_object(self, x, y):
        return self.gb.get_object(x, y)

    def get_object_by_id(self, obj_id):
        result = None

        for char in self.get_characters():
            if char.get_obj_id() == obj_id:
                result = char
                break

        return result

    def get_list_of(self, c):
        """
            Return list of objects of the specified type c ('h' human or 'd' dragon)
        """
        result = None

        if c == 'h':
            result = self.human_list
        elif c == 'd':
            result = self.dragon_list

        return result

    def set_gameboard(self, gb):
        self.gb = gb

    def set_characters_list(self, new_list):
        human_list = []
        dragon_list = []

        for obj in new_list:
            if obj.get_type() == 'h':
                human_list.append(obj)
            elif obj.get_type() == 'd':
                dragon_list.append(obj)

        self.human_list = human_list
        self.dragon_list = dragon_list

    def add_action(self, action):
        """
            Save msg_id in executed_msg_ids
        """
        try:
            self.executed_msg_ids.append(action["msg_id"])
        except:
            print "err:%s" % action

    def add_character(self, obj):
        # if it was previously offline
        obj_id = obj.get_obj_id()
        prev_state = self.get_offline_player_state_by_id(obj_id)
        if prev_state != None:
            print "player %s is back" %(obj_id)
            self.mark_online(obj_id)

        # add to gameboard
        self.gb.set_object(obj, obj.get_x(), obj.get_y())

        # add to our human/dragon list
        if obj.get_type() == 'h':
            self.human_list.append(obj)
        elif obj.get_type() == 'd':
            self.dragon_list.append(obj)

    def remove_character(self, obj):
        # delete from gameboard
        self.gb.del_object(obj.get_x(), obj.get_y())

        # delete from our human/dragon list
        if obj.get_type() == 'h':
            self.human_list.remove(obj)
        elif obj.get_type() == 'd':
            self.dragon_list.remove(obj)

    def attack(self, attacker_id, victim_id):
        attacker = self.get_object_by_id(attacker_id)
        victim = self.get_object_by_id(victim_id)

        if attacker != None and victim != None:
            # first check whether they might be already dead just now
            if self.verbose: print "%s (%d, %d) is attacked by %s (%d damage)" % (victim.get_name(),
                            victim.get_x(), victim.get_y(), attacker.get_name(), attacker.get_ap())

            victim.set_hp(victim.get_hp() - attacker.get_ap())

            if self.verbose: print "..%s's hp is now %d/%d" % (victim.get_name(), victim.get_hp(), victim.get_max_hp())

            if victim.get_hp() <= 0:
                # the victim passed away, very sad..
                if self.verbose: print "..%s (%d, %d) is slained!" % (victim.get_name(), victim.get_x(), victim.get_y())
                self.remove_character(victim)

    def heal(self, healer_id, healed_player_id):
        healer = self.get_object_by_id(healer_id)
        healed_player = self.get_object_by_id(healed_player_id)

        if healer != None and healed_player != None:
            # first check whether they might be already dead just now
            if self.verbose: print "%s (%d, %d) is healed by %s" % (healed_player.get_name(),
                            healed_player.get_x(), healed_player.get_y(), healer.get_name())

            if healed_player.get_hp() + healer.get_ap() > healed_player.get_max_hp():
                # if it healed more than the max hp
                healed_player.set_hp(healed_player.get_max_hp())
            else:
                # if it not, just simply add
                healed_player.set_hp(healed_player.get_hp() + healer.get_ap())

            if self.verbose: print "..%s's hp is now %d/%d" % (healed_player.get_name(),
                            healed_player.get_hp(), healed_player.get_max_hp())

    def move(self, player_id, new_x, new_y):
        player = self.get_object_by_id(player_id)

        if player != None:
            # first check whether it might be already dead just now
            if (abs(player.get_x() - new_x) + abs(player.get_y() - new_y)) == 1:
                # check whether it only moves one step
                obj = self.gb.get_object(new_x, new_y)

                if obj == None:
                    # there is no object on the new coordinate
                    # update the gameboard
                    self.gb.move_object(player.get_x(), player.get_y(), new_x, new_y)

                    # update the character location
                    player.set_x(new_x)
                    player.set_y(new_y)
                else:
                    # there is someone there
                    if self.verbose: print "..blocked by %s (%d, %d)" % (obj.get_name(), obj.get_x(),obj.get_y())

