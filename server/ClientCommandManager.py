import zmq
import json
import time
import uuid
from random import randint
from threading import Thread

from server.TSSModel import TSSModel
from common.JSONEncoder import GameStateEncoder
from common.SocketWrapper import SocketWrapper

class ClientCommandManager(Thread):
    """
        This class is responsible to wait for commands
        submitted to the server's ZMQ REP by clients.
    """
    def __init__(self, tss_model, zmq_context, server_id, client_command_box, server_command_duplicator, command_host):
        Thread.__init__(self)

        self.message_box = client_command_box
        self.tss_model = tss_model
        self.zmq_context = zmq_context
        self.server_id = server_id
        self.server_command_duplicator = server_command_duplicator

        # create ZMQ reply socket for receiving clients' commands
        self.socket = self.zmq_context.socket(zmq.REP)
        self.socket.bind("tcp://%s" % command_host)
        # wrap the socket with timeout capabilities
        self.socket_non_blocking = SocketWrapper(self.socket)

    def run(self):
        while self.tss_model.is_game_running():
            # Wait for next request from client
            # WARNING: the default recv() function is BLOCKING, use with caution!
            # here we use a wrapped non-blocking version
            try:
                json_message = self.socket_non_blocking.recv(timeout=10000)
            except:
                continue

            #  Send ack to client
            self.socket.send(b"{'status' : 'ok'}")

            parsed_message = json.loads(json_message)

            # an event from client arrived, increase our lamport clock
            self.tss_model.increase_event_clock()

            # add lamport clock to our message
            parsed_message["eventstamp"] = self.tss_model.get_event_clock()
            # add local clock to our message
            parsed_message["timestamp"] = self.tss_model.get_current_time()
            # seed the msg_id with our server_id so that it is unique globally
            parsed_message["msg_id"] = uuid.uuid1(self.server_id).hex

            # if a character spawns, randomize spawning location, hp, and ap
            if parsed_message["type"] == "spawn":
                parsed_message = self.process_spawn_msg(parsed_message)

            # save the command for state duplication purposes
            self.message_box.put_message(parsed_message)

            # execute the command right away in the leading state (state_id 0)
            self.tss_model.process_action(parsed_message, state_id=0)

            # duplicate command to peers
            self.server_command_duplicator.publish_msg_to_peers(parsed_message)

        self.socket.close()

    def process_spawn_msg(self, parsed_message):
        # generate randomized x, y, hp and ap for characters in the message

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

        return parsed_message
