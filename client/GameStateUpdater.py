import sys
import zmq
import threading
import time

from common.JSONEncoder import GameStateParser

class GameStateUpdater(threading.Thread):
    def __init__(self, update_delay=200.0):
        threading.Thread.__init__(self)
        self.gamestate = None
        self.update_delay = float(update_delay)
    
        self.context = zmq.Context()
        self.subscriber = self.context.socket(zmq.SUB)
        self.subscriber.connect("tcp://127.0.0.1:8181")
        self.subscriber.setsockopt(zmq.SUBSCRIBE, "")
        # CONFLATE means save only latest message in queue
        self.subscriber.setsockopt(zmq.CONFLATE, 1)

        self.quit_flag = False

    def run(self):
        while self.is_game_running():
            msg = self.subscriber.recv()

            parser = GameStateParser()
            game_running_flag, self.gamestate = parser.parse(msg)

            if game_running_flag == False:
                self.stop_game()

            time.sleep(self.update_delay/1000.0)

        self.subscriber.close()
        self.context.term()

    def stop_game(self):
        self.quit_flag = True

    def is_game_running(self):
        return not self.quit_flag

    def stop(self):
        self.quit_flag = True

    def get_gamestate(self):
        return self.gamestate

    def get_gamestate_in_string(self):
        # make simple representation flattened matrix in a string
        boardstring = ''

        for row in xrange(25):
            for column in xrange(25):
                try:
                    obj = self.gamestate.get_object(row, column)
                except:
                    obj = None
                    
                if obj != None:
                    if obj.get_type() == 'h':
                        boardstring += 'h'
                    elif obj.get_type() == 'd':
                        boardstring += 'd'
                else:
                    boardstring += '.'

        return boardstring
