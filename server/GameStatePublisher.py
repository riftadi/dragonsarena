import zmq
import json
import time
from threading import Thread

from server.TSSModel import TSSModel
from common.JSONEncoder import GameStateEncoder

class GameStatePublisher(Thread):
    """
        This class is responsible to publish game states
        to ZMQ publisher which will be read by clients.
    """
    def __init__(self, tss_model, update_delay=200.0, port_number=8282):
        Thread.__init__(self)

        self.message_box = []
        self.tss_model = tss_model
        self.port_number = port_number
        self.update_delay = update_delay # in milliseconds
        self.finished_flag = False

        # create ZMQ publisher socket for our clients (or observers)
        self.context = zmq.Context()
        self.socket = self.context.socket(zmq.PUB)
        self.socket.bind("tcp://127.0.0.1:%s" % self.port_number)

    def run(self):
        while not self.finished_flag:
            # update message box
            message = {'is_running' : self.tss_model.is_game_running(),
                        'gamestate': self.tss_model.get_gamestate()}

            self.socket.send(json.dumps(message, cls=GameStateEncoder))

            time.sleep(self.update_delay/1000.0)

        self.socket.close()
        self.context.term()

    def stop_publishing(self):
        # it is possible for the game to be finished,
        # but the publisher continue publishing stop message
        self.finished_flag = True
