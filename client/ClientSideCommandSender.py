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
    def __init__(self, zmq_context, command_url):
        # create ZMQ publisher socket for our clients (or observers)
        self.context = zmq_context
        self.socket = self.context.socket(zmq.REQ)
        self.socket.connect("tcp://%s" % command_url)

    def terminate(self):
        self.socket.close()

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
