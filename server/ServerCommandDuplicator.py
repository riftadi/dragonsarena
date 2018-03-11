import zmq
import json
import time
from threading import Thread

from server.TSSModel import TSSModel
from common.JSONEncoder import GameStateEncoder
from common.SocketWrapper import SocketWrapper

class ServerCommandDuplicator(Thread):
    """
        This class is responsible to duplicating commands to peer servers
        using zeroMQ publisher/subscriber message queue.
    """
    def __init__(self, tss_model, zmq_context, client_command_box, server_id, port_number=8383):
        Thread.__init__(self)
        self.peers = [{"name" : "server02", "address" : "192.168.1.102"}]

        self.tss_model = tss_model
        self.zmq_context = zmq_context
        self.message_box = client_command_box
        self.server_id = server_id
        self.port_number = port_number

        # if branching below is just for development purpose with multiple processes in a machine
        if self.server_id == 1:
            # create ZMQ publisher socket to broadcast our messages
            self.socket_pub = self.zmq_context.socket(zmq.PUB)
            self.socket_pub.bind("tcp://127.0.0.1:%d" % 8383)

            # create ZMQ subscriber sockets to subscribe to server02 message
            self.socket_sub02 = self.zmq_context.socket(zmq.SUB)
            self.socket_sub02.connect("tcp://127.0.0.1:%d" % 9393) # local host just for development purpose
            # self.socket.bind("tcp://%s:%s" % (self.peers[0]["address"], self.port_number))
            self.socket_sub02.setsockopt(zmq.SUBSCRIBE, "")
            # wrap the socket with timeout capabilities
            self.socket_sub02_with_timeout = SocketWrapper(self.socket_sub02)
        elif self.server_id == 2:
            # create ZMQ publisher socket to broadcast our messages
            self.socket_pub = self.zmq_context.socket(zmq.PUB)
            self.socket_pub.bind("tcp://127.0.0.1:%d" % 9393)

            # create ZMQ subscriber sockets to subscribe to server02 message
            self.socket_sub01 = self.zmq_context.socket(zmq.SUB)
            self.socket_sub01.connect("tcp://127.0.0.1:%d" % 8383) # local host just for development purpose
            # self.socket.bind("tcp://%s:%s" % (self.peers[0]["address"], self.port_number))
            self.socket_sub01.setsockopt(zmq.SUBSCRIBE, "")
            # wrap the socket with timeout capabilities
            self.socket_sub01_with_timeout = SocketWrapper(self.socket_sub01)

    def run(self):
        while self.tss_model.is_game_running():
            # Listens for messages from peers
            # WARNING: the default recv() function is BLOCKING, use with caution!
            try:
                if self.server_id == 1:
                    json_message = self.socket_sub02_with_timeout.recv(timeout=20000)
                elif self.server_id == 2:
                    json_message = self.socket_sub01_with_timeout.recv(timeout=20000)

                parsed_message = json.loads(json_message)
                # debugging print command
                # print "receiving: %s" % parsed_message

                # save the command in our storage box
                self.message_box.put_message(parsed_message)

                # execute the command in the leading state
                self.tss_model.process_action(parsed_message)
            except:
                pass

        self.socket_pub.close()

        if self.server_id == 1:
            self.socket_sub02.close()
        elif self.server_id == 2:
            self.socket_sub01.close()

    def create_game_start_message(self, start_time):
        msg = {
                "type" : "gamestart",
                "start_time" : start_time,
                "server_id" : self.server_id,
                "timestamp" : self.tss_model.get_current_time()
               }

        # save it to our message_box
        self.message_box.put_message(msg)
        
        # send it to our peers
        self.publish_msg_to_peers(msg)

    def publish_msg_to_peers(self, msg):
        msg["server_id"] = self.server_id
        msg["timestamp"] = self.tss_model.get_current_time()

        self.socket_pub.send(json.dumps(msg, cls=GameStateEncoder))
