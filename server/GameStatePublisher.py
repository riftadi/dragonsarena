import zmq
import json
import time
from threading import Thread

from server.TSSModel import TSSModel
from common.JSONEncoder import GameStateEncoder
from common.settings import *

class GameStatePublisher(Thread):
    """
        This class is responsible to publish game states
        to ZMQ publisher which will be read by clients.
    """
    def __init__(self, tss_model, zmq_context, update_delay=GAMESTATE_PUBLISH_DELAY, publisher="0.0.0.0:8181"):
        Thread.__init__(self)

        self.message_box = []
        self.tss_model = tss_model
        self.zmq_context = zmq_context
        self.update_delay = update_delay # in milliseconds
        self.finished_flag = False

        # create ZMQ publisher socket for our clients (or observers)
        self.socket = self.zmq_context.socket(zmq.PUB)
        self.socket.bind("tcp://%s" % publisher)

    def run(self):
        while not self.finished_flag:
            # send periodic gamestate
            message = {'is_running' : self.tss_model.is_game_running(),
                        'gamestate': self.tss_model.get_leadingstate()}

            s = "gamestate|"+json.dumps(message, cls=GameStateEncoder)
            self.socket.send(s)

            time.sleep(self.update_delay/1000.0)

        self.socket.close()

    def stop_publishing(self):
        # it is possible for the game to be finished,
        # but the publisher continue publishing stop message
        self.finished_flag = True
