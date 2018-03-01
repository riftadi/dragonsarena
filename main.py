#!/usr/bin/python
import time
import pygame
import sys

from TSSEngine import TSSEngine
from UnifiedMessageBox import UnifiedMessageBox
from Bot import *
from Character import *
from GUIDisplay import GUIDisplay

class DragonArena(object):
    """
        Main game class, everything starts here
    """
    def __init__(self, nhuman, ndragon, display_delay=100, verbose=True):
        self.msg_box = UnifiedMessageBox()
        self.M = TSSEngine(25, 25, self.msg_box, verbose=verbose)
        self.timer = 0

        self.M.setName('tss_thread')
        self.M.start()

        self.pl_id = 0
        self.server_id = 10000
        self.plist = []

        self.guidisplay = GUIDisplay(self.M, display_delay)

        for i in xrange(nhuman):
            msg = {"timestamp" : self.M.get_current_time(), "type" : "spawn", "server_id" : self.server_id,
                     "obj_name" : "p%d"%(self.pl_id + 1), "obj_id" : self.server_id+self.pl_id, "obj_type" : "h"}
            self.msg_box.put_message(msg)
            self.plist.append(self.server_id+self.pl_id)
            self.pl_id += 1
        for i in xrange(ndragon):
            msg = {"timestamp" : self.M.get_current_time(), "type" : "spawn", "server_id" : self.server_id,
                     "obj_name" : "d%d"%(self.pl_id + 1), "obj_id" : self.server_id+self.pl_id, "obj_type" : "d"}
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

    def start_game(self):
        self.guidisplay.mainloop()

        self.M.join()
        for bot in self.blist:
            bot.join()

#################################################################
if __name__ == '__main__':
    print "starting dragons arena.."

    if len(sys.argv) == 3:
        human_count = int(sys.argv[1])
        dragon_count = int(sys.argv[2])
    else:
        human_count = 100
        dragon_count = 20

    da = DragonArena(human_count, dragon_count, display_delay=100, verbose=False)

    # start our game
    da.start_game()

    print "game end.."
