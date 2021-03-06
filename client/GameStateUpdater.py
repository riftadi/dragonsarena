import sys
import zmq
import threading
import time

from common.JSONEncoder import GameStateParser
from common.SocketWrapper import SocketWrapper
from common.settings import *

class GameStateUpdater(threading.Thread):
    def __init__(self, zmq_context, update_delay=GAMESTATE_PUBLISH_DELAY, publisher_url="127.0.0.1:8181"):
        threading.Thread.__init__(self)
        self.gamestate = None
        self.update_delay = float(update_delay)

        self.context = zmq_context
        self.subscriber = self.context.socket(zmq.SUB)
        self.subscriber.connect("tcp://%s" % publisher_url)
        # subscribe to gamestate topic
        self.subscriber.setsockopt(zmq.SUBSCRIBE, "gamestate")
        # CONFLATE means save only latest message in queue
        self.subscriber.setsockopt(zmq.CONFLATE, 1)
        self.subscriber_non_blocking = SocketWrapper(self.subscriber)
        self.last_gamestate_update_time = 0
        self.server_timeout_flag = False
        self.counter = 0

        self.quit_flag = False

    def run(self):
        while self.is_game_running():
            # update gamestate periodically
            try:
                message = self.subscriber_non_blocking.recv(timeout=CLIENTSIDE_UPDATE_TIMEOUT)
            except:
                print "timeout"
                self.server_timeout_flag = True
                continue

            if message.startswith("gamestate|") == True:
                now = int(round(time.time() * 1000))
                self.last_gamestate_update_time = now
                msg = message[10:]
                parser = GameStateParser()
                game_running_flag, self.gamestate = parser.parse(msg)

                if game_running_flag == False:
                    self.stop()
                self.counter = self.counter + 1

            # other topic goes here, if any

            time.sleep(self.update_delay/1000.0)

        self.subscriber.close()

    def received(self):
        if self.counter > 0:
            return True
        return False

    def is_server_timeout(self):
        return self.server_timeout_flag

    def is_game_running(self):
        return not self.quit_flag

    def stop(self):
        self.quit_flag = True

    def get_last_gamestate_update_time(self):
        return self.last_gamestate_update_time

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
