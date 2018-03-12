import zmq
import json
import time
from threading import Thread

from server.TSSModel import TSSModel
from common.JSONEncoder import GameStateEncoder
from common.SocketWrapper import SocketWrapper

class ClientCommandManager(Thread):
    """
        This class is responsible to publish game states
        to ZMQ publisher which will be read by clients.
    """
    def __init__(self, tss_model, client_command_box, port_number=8282):
        Thread.__init__(self)

        self.message_box = client_command_box
        self.tss_model = tss_model
        self.port_number = port_number

        # create ZMQ publisher socket for our clients (or observers)
        self.context = zmq.Context()
        self.socket = self.context.socket(zmq.REP)
        self.socket.bind("tcp://127.0.0.1:%s" % self.port_number)
        # wrap the socket with timeout capabilities
        self.socket_non_blocking = SocketWrapper(self.socket)

    def run(self):
        while self.tss_model.is_game_running():
            # Wait for next request from client
            # WARNING: this recv() function is BLOCKING, use with caution!
            try:
                json_message = self.socket_non_blocking.recv(timeout=10000)

                #  Send ack to client
                self.socket.send(b"{'status' : 'ok'}")

                parsed_message = json.loads(json_message)
                parsed_message["timestamp"] = self.tss_model.get_current_time()

                # save the command for state duplication purposes
                self.message_box.put_message(parsed_message)

                # execute the command in the leading state
                self.tss_model.process_action(parsed_message)
            except:
                pass

        self.socket.close()
        self.context.term()

