import zmq
import json
import time
from random import randint
from threading import Thread

from server.TSSModel import TSSModel
from common.JSONEncoder import GameStateEncoder
from common.SocketWrapper import SocketWrapper

class ClientCommandManager(Thread):
    """
        This class is responsible to publish game states
        to ZMQ publisher which will be read by clients.
    """
    def __init__(self, tss_model, zmq_context, server_id, client_command_box, server_state_duplicator, port_number=8282):
        Thread.__init__(self)

        self.message_box = client_command_box
        self.tss_model = tss_model
        self.zmq_context = zmq_context
        self.server_id = server_id
        self.server_state_duplicator = server_state_duplicator
        self.port_number = port_number

        # create ZMQ reply socket for receiving clients' commands
        self.socket = self.zmq_context.socket(zmq.REP)
        self.socket.bind("tcp://127.0.0.1:%s" % self.port_number)
        # wrap the socket with timeout capabilities
        self.socket_non_blocking = SocketWrapper(self.socket)

    def run(self):
        while self.tss_model.is_game_running():
            # Wait for next request from client
            # WARNING: the default recv() function is BLOCKING, use with caution!
            # here we use a wrapped non-blocking version
            try:
                json_message = self.socket_non_blocking.recv(timeout=10000)

                #  Send ack to client
                self.socket.send(b"{'status' : 'ok'}")

                parsed_message = json.loads(json_message)
                parsed_message["timestamp"] = self.tss_model.get_current_time()
                parsed_message["server_id"] = self.server_id

                # if a character spawns, randomize spawning location, hp, and ap
                if parsed_message["type"] == "spawn":
                    if parsed_message["player_type"] == "human":
                        parsed_message["hp"] = randint(11,20)
                        parsed_message["ap"] = randint(1,10)
                    elif parsed_message["player_type"] == "dragon":
                        parsed_message["hp"] = randint(50,100)
                        parsed_message["ap"] = randint(5,20)

                    safely_placed = False
                    while not safely_placed:
                        prop_x = randint(0, 24)
                        prop_y = randint(0, 24)

                        if self.tss_model.get_object(prop_x, prop_y) == None:
                            safely_placed = True
                            parsed_message["x"] = prop_x
                            parsed_message["y"] = prop_y

                # execute the command in the leading state
                self.tss_model.process_action(parsed_message)

                # duplicate command to peers
                self.server_state_duplicator.publish_msg_to_peers(parsed_message)

                # save the command for state duplication purposes
                self.message_box.put_message(parsed_message)
            except:
                pass

        self.socket.close()
