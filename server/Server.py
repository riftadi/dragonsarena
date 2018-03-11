import time
import zmq

from server.TSSModel import TSSModel
from server.ClientMessageBox import ClientMessageBox
from server.GameClockManager import GameClockManager
from server.ClientCommandManager import ClientCommandManager
from server.GameStatePublisher import GameStatePublisher
from server.ServerCommandDuplicator import ServerCommandDuplicator

class Server(object):
    def __init__(self, server_id, verbose=True):
        self.server_id = server_id
        self.verbose = verbose
        # get start time in milliseconds since epoch
        self.absolute_game_start_time = int(round(time.time() * 1000))
        self.zmq_root_context = zmq.Context()

        self.port_number = [[8181, 8282, 8383], [9191, 9292, 9393]]

        # MODELLER CLASSES INSTANTIATION
        # start TSS boards representation
        self.T = TSSModel(width=25, height=25, start_time=self.absolute_game_start_time, verbose=self.verbose)

        # start client message storage box
        self.clients_cmds_box = ClientMessageBox()

        ############################################

        # CONTROLLER (WORKER) CLASSES INSTANTIATION
        # start clock and winning condition updater worker
        self.clock_winning_worker = GameClockManager(self.T, self.clients_cmds_box, update_delay=10.0)
        self.clock_winning_worker.start()

        # start client facing game state publisher
        self.publisher_worker = GameStatePublisher(self.T, self.zmq_root_context, port_number=self.port_number[self.server_id-1][0])
        self.publisher_worker.start()

        # start server to server communication engine
        # --TODO-- implement server to server communication classes
        self.server_cmd_duplicator_worker = ServerCommandDuplicator(self.T, self.zmq_root_context, self.clients_cmds_box,
                    self.server_id, port_number=self.port_number[self.server_id-1][2])
        self.server_cmd_duplicator_worker.start()
        self.server_cmd_duplicator_worker.create_game_start_message(self.absolute_game_start_time)

        # start client commands worker
        self.client_command_worker = ClientCommandManager(self.T, self.zmq_root_context, self.server_id, self.clients_cmds_box,
            self.server_cmd_duplicator_worker, port_number=self.port_number[self.server_id-1][1])
        self.client_command_worker.start()

    def mainloop(self):
        while self.T.is_game_running():
            # just sleep for 500ms while checking if the game is still running
            time.sleep(500.0/1000.0)

        print "Ending games.."
        # give a few seconds delay to give opportunity for publisher_worker to broadcast
        # that the game is already finished
        time.sleep(5)
        self.publisher_worker.stop_publishing()

        # game is finished, cleaning up worker threads
        self.client_command_worker.join()
        self.publisher_worker.join()
        self.clock_winning_worker.join()
        
        self.zmq_root_context.term()
