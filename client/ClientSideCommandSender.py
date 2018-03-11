import zmq
import json
import time
import json
from threading import Thread

from common.JSONEncoder import GameStateEncoder

class ClientSideCommandSender(object):
    """
        This class is responsible to publish game states
        to ZMQ publisher which will be read by clients.
    """
    def __init__(self, port_number=8282):
        self.port_number = port_number

        # create ZMQ publisher socket for our clients (or observers)
        self.context = zmq.Context()
        self.socket = self.context.socket(zmq.REQ)
        self.socket.connect("tcp://127.0.0.1:%s" % self.port_number)

    def terminate(self):
        self.socket.close()
        self.context.term()

    def send_message(self, message):
        if isinstance(message, dict):
            json_message = json.dumps(message)
        if isinstance(message, str):
            json_message = message

        self.socket.send(json_message)
        self.process_reply()

    def process_reply(self):
        response = self.socket.recv()
        # print "Received reply %s [ %s ]" % (json_message, response)
