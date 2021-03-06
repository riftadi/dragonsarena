import zmq
import json
import logging
import time
import uuid
from threading import Thread

from server.TSSModel import TSSModel
from common.JSONEncoder import GameStateEncoder
from common.SocketWrapper import SocketWrapper
from common.settings import *

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
                json_message = self.socket_non_blocking.recv(timeout=5000)
            except:
                continue

            #  Send ack to client
            self.socket.send(b"{'status' : 'ok'}")

            parsed_message = json.loads(json_message)
            # update client last seen time
            self.tss_model.update_client_last_seen_time(parsed_message["player_id"])

            # an event from client arrived, increase our lamport clock
            self.tss_model.increase_event_clock()

            # add lamport clock to our message
            parsed_message["eventstamp"] = self.tss_model.get_event_clock()
            # add local clock to our message
            parsed_message["timestamp"] = int(round(time.time() * 1000))
            # seed the msg_id with our server_id so that it is unique globally
            parsed_message["msg_id"] = uuid.uuid1(self.server_id).hex

            # if a character spawns, randomize spawning location, hp, and ap
            if parsed_message["type"] == "spawn":
                parsed_message = self.server_command_duplicator.process_spawn_msg(parsed_message)
                parsed_message["type"] = "proposal"
                player_id = parsed_message["player_id"]
                self.tss_model.lock_cell(parsed_message)
                self.server_command_duplicator.init_vote(player_id)
                self.server_command_duplicator.publish_spawn(parsed_message)
            else:
                # save the command for state duplication purposes
                self.message_box.put_message(parsed_message)

                # execute the command right away in the leading state
                self.tss_model.process_action(parsed_message, state_id=LEADING_STATE)
                
                # duplicate command to peers
                self.server_command_duplicator.publish_msg_to_peers(parsed_message)

        self.socket.close()
