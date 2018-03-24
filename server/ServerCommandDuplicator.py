import zmq
import json
import time
import uuid
from threading import Thread, Lock
from random import randint

from server.TSSModel import TSSModel
from common.JSONEncoder import GameStateEncoder
from common.SocketWrapper import SocketWrapper
from common.settings import *

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
        self.votes = {}
        self.lock = Lock()
        self.last_msg_timestamp = 0

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

                        self.tss_model.update_client_last_seen_time(parsed_message["player_id"])

                        # process the message
                        self.process_message(parsed_message)

                    elif message.startswith("alive|") == True:
                        self.heartbeat[subscription.LAST_ENDPOINT[6:]] = time.time()

                    elif message.startswith("spawn|") == True:
                        parsed_message = json.loads(message[6:])
                        if parsed_message["type"] == "proposal":
                            x = parsed_message["x"]
                            y = parsed_message["y"]
                            player_id = parsed_message["player_id"]
                            # check if coordinates are occupied and not locked
                            free = self.tss_model.get_object(x,y) is None and self.tss_model.collide_with_locked(x, y) is False
                            vote = False
                            if free is True:
                                self.tss_model.lock_cell(parsed_message)
                                vote = True

                            self.publish_spawn({
                                "type": "vote",
                                "vote": vote,
                                "player_id": player_id
                            })
                        elif parsed_message["type"] == "vote":
                            vote = parsed_message["vote"]
                            player_id = parsed_message["player_id"]

                            if self.votes.has_key(player_id) == True:
                                if vote == False:
                                    old_message = self.tss_model.get_locked(player_id)
                                    self.tss_model.unlock_cell(player_id)
                                    self.lock.acquire()
                                    del self.votes[player_id]
                                    self.lock.release()
                                    # Abort current round
                                    self.publish_spawn({
                                        "type": "commit",
                                        "success": False,
                                        "player_id": player_id
                                    })
                                    # start new vote
                                    new_proposal = self.process_spawn_msg(old_message)
                                    self.tss_model.lock_cell(new_proposal)
                                    self.init_vote(player_id)
                                    self.publish_spawn(new_proposal)

                                else:
                                    self.add_vote(player_id, subscription.LAST_ENDPOINT[6:])
                        elif parsed_message["type"] == "commit":
                            success = parsed_message["success"]
                            player_id = parsed_message["player_id"]
                            if success == False:
                                self.tss_model.unlock_cell(player_id)
                            else:
                                # spawning, increment our lamport clock
                                self.tss_model.increase_event_clock()

                                proposal_msg = self.tss_model.get_locked(player_id)
                                proposal_msg["timestamp"] = parsed_message["timestamp"]
                                proposal_msg["eventstamp"] = parsed_message["eventstamp"]
                                proposal_msg["msg_id"] = uuid.uuid1(self.server_id).hex
                                proposal_msg["type"] = "spawn"

                                # process the message
                                self.process_message(proposal_msg)
                    # other topic goes here
            
            now = int(round(time.time() * 1000))
            if now - last_alive_in_ms > 100:
                self.publish_alive()
                last_alive_in_ms = now
            self.check_peers()
            self.check_votes()

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

    def check_votes(self):
        if len(self.votes) == 0:
            return
        self.lock.acquire()
        done = []
        for player_id, votes in self.votes.iteritems():
            if len(votes) == 0:
                continue

            all_received = True

            for server, connection in self.subscriptions.iteritems():
                if connection is None:
                    continue

                host = connection.LAST_ENDPOINT[6:]
                if host not in votes:
                    all_received = False
                    break

            if all_received is True:
                done.append(player_id)  

        for player_id in done:
            # message for local spawning via TSS
            proposal_msg = self.tss_model.get_locked(player_id)
            
            # add lamport clock to our message
            proposal_msg["eventstamp"] = self.tss_model.get_event_clock()
            # add local clock to our message
            proposal_msg["timestamp"] = int(round(time.time() * 1000))
            proposal_msg["type"] = "spawn"

            # process the message
            self.process_message(proposal_msg)

            del self.votes[player_id]
            self.publish_spawn({
                "type": "commit",
                "success": True,
                "player_id": player_id,
                "timestamp": proposal_msg["timestamp"],
                "eventstamp": proposal_msg["eventstamp"]
            })
        self.lock.release()

    def process_message(self, action_msg):
        # save the command for state duplication purposes
        self.message_box.put_message(action_msg)

        # execute the command if the timestamp of the message is newer than last message
        if action_msg["timestamp"] >= self.last_msg_timestamp-MSG_LATE_DELAY_BUDGET:
            self.tss_model.process_action(action_msg, state_id=LEADING_STATE)
            self.last_msg_timestamp = action_msg["timestamp"]

    def add_vote(self, player_id, connection):
        self.lock.acquire()
        if self.votes.has_key(player_id):
            self.votes[player_id].append(connection)
        else:
            self.votes[player_id] = [connection]
        self.lock.release()

    def init_vote(self, player_id):
        self.lock.acquire()
        self.votes[player_id] = []
        self.lock.release()

    def publish_spawn(self, msg):
        msg["msg_id"] = uuid.uuid1(self.server_id).hex
        message = "spawn|" + json.dumps(msg)
        self.publisher.send(message)

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
            "timestamp" : self.tss_model.get_current_time(),
            "msg_id" : uuid.uuid1(self.server_id).hex
        }
        try:
            self.publisher.send("alive|")
        except:
            pass

    def process_spawn_msg(self, parsed_message):
        # generate randomized x, y, hp and ap for characters in the message

        # check if it's offline before
        prev_state = self.tss_model.get_offline_player_state_by_id(parsed_message["player_id"])
        if prev_state != None:
            # it is a returning client, get its information back
            parsed_message["hp"] = prev_state["hp"]
            parsed_message["max_hp"] = prev_state["max_hp"]
            parsed_message["ap"] = prev_state["ap"]
            parsed_message["player_type"] = prev_state["type"]
            # ignore previous state location info as they might be used by another character

        else:
            # it's a new character
            if parsed_message["player_type"] == "h":
                parsed_message["hp"] = randint(11,20)
                parsed_message["max_hp"] = parsed_message["hp"]
                parsed_message["ap"] = randint(1,10)
            elif parsed_message["player_type"] == "d":
                parsed_message["hp"] = randint(50,100)
                parsed_message["max_hp"] = parsed_message["hp"]
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