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
    def __init__(self, tss_model, zmq_context, client_command_box, server_id, host, peers):
        Thread.__init__(self)
        self.tss_model = tss_model
        self.zmq_context = zmq_context
        self.message_box = client_command_box
        self.server_id = server_id
        self.subscriptions = {}
        self.heartbeat = {}

        #create ZMQ publisher socket to broadcast our messages
        self.publisher = self.zmq_context.socket(zmq.PUB)
        self.publisher.bind("tcp://%s" % host["server2server"])

        #create ZMQ subscriber for each peer servers
        for server in peers:
            connection = self.zmq_context.socket(zmq.SUB)
            connection.connect("tcp://%s" % server["server2server"])
            connection.setsockopt(zmq.SUBSCRIBE, "command")
            connection.setsockopt(zmq.SUBSCRIBE, "alive")
            connection.setsockopt(zmq.SUBSCRIBE, "spawn")
            self.subscriptions[server["server2server"]] = connection

    def run(self):
        last_alive_in_ms = int(round(time.time() * 1000))
        while self.tss_model.is_game_running():
            # Listens for messages from peers
            # based on http://zguide.zeromq.org/py:msreader
            for subscription in self.subscriptions.itervalues():
                if subscription is None:
                    continue

                while True:
                    try:
                        message = subscription.recv(zmq.DONTWAIT)
                    except zmq.Again:
                        break

                    if message.startswith("command|") == True:
                        parsed_message = json.loads(message[8:])
                        # debugging print command
                        # print "receiving: %s" % parsed_message

                        # save the command in our storage box
                        self.message_box.put_message(parsed_message)

                        # execute the command in the leading state
                        self.tss_model.process_action(parsed_message)

                    if message.startswith("alive|") == True:
                        self.heartbeat[subscription.LAST_ENDPOINT[6:]] = time.time()

                    # other topic goes here
            now = int(round(time.time() * 1000))
            if now - last_alive_in_ms > 100:
                self.publish_alive()
                last_alive_in_ms = now
            self.check_peers()

        # end of the game running loop

        self.publisher.close()

        for subscription in self.subscriptions.itervalues():
            if subscription is None:
                continue
            subscription.close()

    def check_peers(self):
        now = time.time()

        for key, timestamp in self.heartbeat.iteritems():
            if timestamp is None:
                continue
            if now - timestamp > 1:
                self.heartbeat[key] = None
                print "shuting down " + key
                self.subscriptions[key].close()
                self.subscriptions[key] = None


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

        s = "command|"+json.dumps(msg, cls=GameStateEncoder)
        self.publisher.send(s)

    def publish_alive(self):
        msg = {
            "timestamp": self.tss_model.get_current_time()
        }
        self.publisher.send("alive|")
