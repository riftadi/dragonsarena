import time
import zmq

from client.bot.Bot import HumanBot, DragonBot
from client.ClientSideCommandSender import ClientSideCommandSender
from client.GameStateUpdater import GameStateUpdater

class Client(object):
    def __init__(self, server_id, player_type, player_id, verbose=True):
        self.server_id = server_id
        
        target_url = ["127.0.0.1:8181", "127.0.0.1:8282"]
        if self.server_id == 2:
            target_url = ["127.0.0.1:9191", "127.0.0.1:9292"]

        self.zmq_root_context = zmq.Context()


        self.gsu = GameStateUpdater(self.zmq_root_context, target_url=target_url[0])
        self.gsu.start()

        self.msg_sender = ClientSideCommandSender(self.zmq_root_context, target_url=target_url[1])

        # spawn our character
        self.player_id = player_id
        self.player_type = player_type
        self.spawn_character()

        self.verbose = verbose

        # start our bot (automatic controller)
        if self.player_type == "human":
            self.bot = HumanBot(self.player_id, self.msg_sender, self.gsu, self.verbose)
        else:
            self.bot = DragonBot(self.player_id, self.msg_sender, self.gsu, self.verbose)
        self.bot.start()

    def spawn_character(self):
        msg = {
            "type" : "spawn",
            "player_id" : self.player_id,
            "player_type" : self.player_type
        }

        self.msg_sender.send_message(msg)

    def wait_for_initial_gamestate(self):
        while self.gsu.get_gamestate() == None:
            time.sleep(0.2)

    def update_bot_gamestate(self):
        self.bot.update_gamestate()

    def is_game_running(self):
        return self.gsu.is_game_running()

    def is_char_alive(self):
        return self.bot.is_char_alive()

    def stop_gamestate_updater(self):
        self.gsu.stop()

    def terminate(self):
        self.msg_sender.terminate()
        self.bot.join()
        self.gsu.join()

        self.zmq_root_context.term()
