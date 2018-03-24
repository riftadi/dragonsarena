import time
import zmq

from client.bot.Bot import HumanBot, DragonBot
from client.ClientSideCommandSender import ClientSideCommandSender
from client.GameStateUpdater import GameStateUpdater
from common.settings import *

class Client(object):
    def __init__(self, publisher_url, command_url, player_type, player_id, zmq_context=None, verbose=True):
        self.publisher_url = publisher_url
        self.command_url = command_url

        self.zmq_context_initated_flag = True
        if zmq_context == None:
            self.zmq_root_context = zmq.Context()
        else:
            self.zmq_root_context = zmq_context
            self.zmq_context_initated_flag = False

        self.gsu = GameStateUpdater(self.zmq_root_context, publisher_url=self.publisher_url)
        self.gsu.start()

        self.msg_sender = ClientSideCommandSender(self.zmq_root_context, command_url=self.command_url)

        # spawn our character
        self.player_id = player_id
        self.player_type = player_type[0] # only pick its first char ('h' or 'd')
        self.spawn_character()

        self.verbose = verbose

        # start our bot (automatic controller)
        if self.player_type == 'h':
            self.bot = HumanBot(self.player_id, self.msg_sender, self.gsu, self.verbose)
        elif self.player_type == 'd':
            self.bot = DragonBot(self.player_id, self.msg_sender, self.gsu, self.verbose)
        self.bot.start()

    def change_server(self, new_publisher_url, new_command_url):
        # change server to a new one
        self.publisher_url = new_publisher_url
        self.command_url = new_command_url

        # destroy old workers
        self.msg_sender.terminate()
        self.stop_gamestate_updater()
        self.gsu.join()

        # start new one
        self.gsu = GameStateUpdater(self.zmq_root_context, publisher_url=self.publisher_url)
        self.gsu.start()
        self.msg_sender = ClientSideCommandSender(self.zmq_root_context, command_url=self.command_url)

        # update bot
        self.bot.change_workers(self.msg_sender, self.gsu)

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

    def is_server_timeout(self):
        return self.gsu.is_server_timeout()

    def stop_gamestate_updater(self):
        self.gsu.stop()

    def terminate(self):
        self.msg_sender.terminate()
        self.bot.join()
        self.gsu.join()

        if self.zmq_context_initated_flag:
            self.zmq_root_context.term()
