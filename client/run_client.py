#!/usr/bin/python
import sys
import time
import uuid
from random import randint

from client.Client import Client
from common.settings import *

VERBOSE = False

if __name__ == '__main__':
    # by default the type is human, unless specified otherwise
    player_type = "human"
    player_id = uuid.uuid4().hex

    if len(sys.argv) == 2:
        player_type = sys.argv[1]

    servers_list = SERVERS_LOCAL

    rand_idx = randint(0, len(CLIENTSIDE_SERVER_LIST)-1)
    server_id = CLIENTSIDE_SERVER_LIST[rand_idx]

    # find out our server info
    server = {}
    for s in servers_list:
        if s["server_id"] == server_id:
            # we got our server
            server = s
            break
    
    print "Starting client for %s with id %s, connecting to server %d" % (player_type, player_id, server_id)

    # start our client
    c = Client(publisher_url=server["server2client"], command_url=server["client2server"],
                player_type=player_type, player_id=player_id, verbose=VERBOSE)

    # wait a bit and let the gamestate comes in
    c.wait_for_initial_gamestate()

    while c.is_game_running() and c.is_char_alive():
        c.update_bot_gamestate()
        time.sleep(1)

    c.stop_gamestate_updater()
    c.terminate()
    print "Exiting client for %s with %s.." % (player_type, player_id)
