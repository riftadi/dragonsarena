import threading
from client.Client import Client
from common.settings import *
from random import randint
import time

class ClientThread(threading.Thread):
    def __init__(self, uid, zmq_context):
        threading.Thread.__init__(self)
        self.rand_idx = randint(0, len(CLIENTSIDE_SERVER_LIST)-1)
        self.server_id = CLIENTSIDE_SERVER_LIST[self.rand_idx]
        self.id = uid
        self.servers = SERVERS_LOCAL
        self.online = True
        self.server = self.get_server_info(self.server_id, self.servers)
        self.zmq_context = zmq_context

        #print "Starting client for %s with id %s, connecting to server %d" % ("human", self.id, self.server_id)
        self.c = Client(publisher_url=self.server["server2client"], command_url=self.server["client2server"],
                player_type="human", player_id=self.id, zmq_context=zmq_context, verbose=False)
    
    def get_server_info(self,server_id, servers_list):
        server = {}
        for s in servers_list:
            if s["server_id"] == server_id:
                # we got our server
                server = s
                break
        return server

    def set_offline(self):
        self.online = False

    def run(self):
        while self.online and self.c.is_game_running() and self.c.is_char_alive():
            if self.c.is_server_timeout():
                # existing server does not send updates
                #print "player %s: server %d does not send any update, finding another server.." % (self.id, self.server_id)
                # find a new server
                new_rand_idx = self.rand_idx
                while new_rand_idx == self.rand_idx:
                    new_rand_idx = randint(0, len(CLIENTSIDE_SERVER_LIST)-1)

                self.server_id = CLIENTSIDE_SERVER_LIST[new_rand_idx]
                self.server = self.get_server_info(self.server_id, self.servers)

                print "player %s: connecting to new server %d.." % (self.id, self.server_id)
                # connect to new server
                self.c.change_server(new_publisher_url=self.server["server2client"], new_command_url=self.server["client2server"])

            self.c.update_bot_gamestate()
            time.sleep(1)

        self.c.stop_gamestate_updater()
        self.c.terminate()
        #print "Exiting client for %s with %s.." % ("human", self.id)

