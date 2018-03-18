import zmq
import json
import time
import uuid
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

                    # we receive a new message from a peer!
                    if message.startswith("command|") == True:
                        parsed_message = json.loads(message[8:])
                        # debugging print command
                        # print "receiving: %s" % parsed_message

                        # update our lamport clock
                        curr_clock = self.tss_model.get_event_clock()
                        msg_clock = parsed_message["eventstamp"]
                        new_clock = max(curr_clock, msg_clock) + 1
                        self.tss_model.set_event_clock(new_clock)

                        # save the command for state duplication purposes
                        self.message_box.put_message(parsed_message)

                        # execute the command in the leading state if the delay is within 200ms
                        now = int(round(time.time() * 1000))
                        if abs(now - parsed_message["timestamp"]) < 200:
                            self.tss_model.process_action(parsed_message, state_id=0)

                    if message.startswith("alive|") == True:
                        self.heartbeat[subscription.LAST_ENDPOINT[6:]] = time.time()

                    # other topic goes here
            
            now = int(round(time.time() * 1000))
            if now - last_alive_in_ms > 100:
                self.publish_alive()
                last_alive_in_ms = now
            self.check_peers()

        # end of the game running loop
        for subscription in self.subscriptions.itervalues():
            if subscription is None:
                continue
            subscription.close()

        self.publisher.close()

    def check_peers(self):
        now = time.time()

        for key, timestamp in self.heartbeat.iteritems():
            if timestamp is None:
                continue
            if now - timestamp > 1:
                self.heartbeat[key] = None
                # print "shuting down " + key
                self.subscriptions[key].close()
                self.subscriptions[key] = None

    def publish_msg_to_peers(self, msg):
        s = "command|"+json.dumps(msg, cls=GameStateEncoder)

        try:
            # if self.server_id == 2:
            #     # simulate late message sending in server 2
            #     time.sleep(0.1)
            self.publisher.send(s)
        except:
            pass

    def publish_alive(self):
        msg = {
            "timestamp": self.tss_model.get_current_time()
        }
        try:
            self.publisher.send("alive|")
        except:
            pass
