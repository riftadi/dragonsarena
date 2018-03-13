#!/usr/bin/python
import sys
import time
import uuid
from random import randint

from client.Client import Client

VERBOSE = False
server_file = "server.txt"
servers = []

if __name__ == '__main__':
    # by default the type is human, unless specified otherwise
    player_type = "human"
    player_id = uuid.uuid4().hex

    if len(sys.argv) == 2:
        player_type = sys.argv[1]

    with open(server_file) as f:
        next(f)
        for line in f:
            server_adresses = line.strip().split(",")
            servers.append({
                "client2server": server_adresses[0],
                "server2client": server_adresses[1],
                "server2server": server_adresses[2]
            })

    server = servers[randint(0, len(servers) - 1)]

    print "Starting client for %s with id %s.." % (player_type, player_id)

    # start our client
    c = Client(publisher_url=server["server2client"], command_url=server["client2server"], player_type=player_type, player_id=player_id, verbose=VERBOSE)

    # let the gamestate comes in
    c.wait_for_initial_gamestate()

    while c.is_game_running() and c.is_char_alive():
        c.update_bot_gamestate()
        time.sleep(1)

    c.stop_gamestate_updater()
    c.terminate()
    print "Exiting client for %s with %s.." % (player_type, player_id)
