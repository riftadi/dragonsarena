#!/usr/bin/python
import sys
import time
import uuid

from client.Client import Client

VERBOSE = False

if __name__ == '__main__':
    # by default the type is human, unless specified otherwise
    player_type = "human"
    player_id = uuid.uuid4().hex

    if len(sys.argv) == 3:
        publisher_url = sys.argv[1]
        command_url = sys.argv[2]

    if len(sys.argv) == 4:
        publisher_url = sys.argv[1]
        command_url = sys.argv[2]
        player_type = sys.argv[3]

    print "Starting client for %s with id %s.." % (player_type, player_id)

    # start our client
    c = Client(publisher_url=publisher_url, command_url=command_url, player_type=player_type, player_id=player_id, verbose=VERBOSE)

    # let the gamestate comes in
    c.wait_for_initial_gamestate()

    while c.is_game_running() and c.is_char_alive():
        c.update_bot_gamestate()
        time.sleep(1)

    c.stop_gamestate_updater()
    c.terminate()
    print "Exiting client for %s with %s.." % (player_type, player_id)
