#!/usr/bin/python
import sys
import time
import uuid
from random import randint
import zmq

from client.Client import Client
from common.settings import *

VERBOSE = False

def get_server_info(server_id, servers_list):
    server = {}
    for s in servers_list:
        if s["server_id"] == server_id:
            # we got our server
            server = s
            break
    return server

if __name__ == '__main__':
    # by default the type is human, unless specified otherwise
    player_type = "human"
    player_id = uuid.uuid4().hex
    zmq_root_context = zmq.Context()

    if len(sys.argv) == 2:
        player_type = sys.argv[1]

    if AWS_MODE_FLAG:
        servers_list = SERVERS_AWS_PUBLIC
    else:
        servers_list = SERVERS_LOCAL

    rand_idx = randint(0, len(CLIENTSIDE_SERVER_LIST)-1)
    server_id = CLIENTSIDE_SERVER_LIST[rand_idx]

    # find out our server info
    server = get_server_info(server_id, servers_list)
    
    print "Starting client for %s with id %s, connecting to server %d" % (player_type, player_id, server_id)

    # start our client
    c = Client(publisher_url=server["server2client"], command_url=server["client2server"],
                player_type=player_type, player_id=player_id, zmq_context=zmq_root_context, verbose=VERBOSE)

    # wait a bit and let the gamestate comes in
    # c.wait_for_initial_gamestate()

    while c.is_game_running() and c.is_char_alive():
        if c.is_server_timeout():
            # existing server does not send updates
            print "player %s: server %d does not send any update, finding another server.." % (player_id, server_id)
            # find a new server
            new_rand_idx = rand_idx
            while new_rand_idx == rand_idx:
                new_rand_idx = randint(0, len(CLIENTSIDE_SERVER_LIST)-1)

            server_id = CLIENTSIDE_SERVER_LIST[new_rand_idx]
            server = get_server_info(server_id, servers_list)

            print "player %s: connecting to new server %d.." % (player_id, server_id)
            # connect to new server
            c.change_server(new_publisher_url=server["server2client"], new_command_url=server["client2server"])

            # wait a bit and let the gamestate comes in
            # c.wait_for_initial_gamestate()

        c.update_bot_gamestate()
        time.sleep(1)

    c.stop_gamestate_updater()
    c.terminate()
    zmq_root_context.term()
    print "Exiting client for %s with %s.." % (player_type, player_id)
