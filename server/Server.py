import time
import zmq

from server.TSSModel import TSSModel
from server.MessageBox import MessageBox
from server.GameClockManager import GameClockManager
from server.ClientCommandManager import ClientCommandManager
from server.GameStatePublisher import GameStatePublisher
from server.ServerCommandDuplicator import ServerCommandDuplicator
from server.TSSManager import TSSManager
from common.settings import *

class Server(object):
    def __init__(self, server_id, host, peers, verbose=True):
        self.server_id = server_id
        self.verbose = verbose
        # get start time in milliseconds since epoch
        self.absolute_game_start_time = int(round(time.time() * 1000))
        self.zmq_root_context = zmq.Context()

        self.peers = peers
        self.host = host

        # MODELLER CLASSES INSTANTIATION
        # start TSS boards representation
        self.T = TSSModel(width=25, height=25, start_time=self.absolute_game_start_time, verbose=self.verbose)

        # start message storage box
        self.msg_box = MessageBox()

        ############################################

        # CONTROLLER (WORKER) CLASSES INSTANTIATION
        # start clock and winning condition updater worker
        self.clock_winning_worker = GameClockManager(self.T, self.msg_box, update_delay=GAMECLOCK_UPDATE_DELAY)
        self.clock_winning_worker.start()

        # start client facing game state publisher
        self.publisher_worker = GameStatePublisher(self.T, self.zmq_root_context, publisher=self.host["server2client"])
        self.publisher_worker.start()

        # start server to server communication engine
        self.server_cmd_duplicator_worker = ServerCommandDuplicator(self.T, self.zmq_root_context, self.msg_box,
                    self.server_id, host=host, peers=peers)
        self.server_cmd_duplicator_worker.start()

        # start client commands worker
        self.client_command_worker = ClientCommandManager(self.T, self.zmq_root_context, self.server_id, self.msg_box,
            self.server_cmd_duplicator_worker, command_host=self.host["client2server"])
        self.client_command_worker.start()

        # start TSS worker
        self.tss_worker = TSSManager(self.T, self.msg_box, self.absolute_game_start_time)
        self.tss_worker.start()

    def mainloop(self):
        while self.T.is_game_running():
            # just sleep for SERVER_MAIN_LOOP_DELAY while checking if the game is still running
            time.sleep(SERVER_MAIN_LOOP_DELAY/1000.0)

        print "Ending games.."
        # give a few seconds delay to give opportunity for publisher_worker to broadcast
        # that the game is already finished
        time.sleep(WAIT_DELAY_AFTER_GAME_END/1000)
        self.publisher_worker.stop_publishing()

        # game is finished, cleaning up worker threads
        self.tss_worker.join()
        self.client_command_worker.join()
        self.publisher_worker.join()
        self.clock_winning_worker.join()
        
        self.zmq_root_context.term()
