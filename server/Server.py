import time

from server.TSSModel import TSSModel
from server.ClientMessageBox import ClientMessageBox
from server.GameClockManager import GameClockManager
from server.ClientCommandManager import ClientCommandManager
from server.GameStatePublisher import GameStatePublisher


class Server(object):
    def __init__(self, server_id, verbose=True):
        self.server_id = server_id
        self.verbose = verbose

        # MODELLER CLASSES INSTANTIATION
        # start TSS boards representation
        self.T = TSSModel(width=25, height=25, verbose=self.verbose)

        # start client facing message box
        self.clients_cmds_box = ClientMessageBox()

        ############################################

        # CONTROLLER (WORKER) CLASSES INSTANTIATION
        # start clock and winning condition updater worker
        self.clock_winning_worker = GameClockManager(self.T, self.clients_cmds_box, update_delay=10.0)
        self.clock_winning_worker.start()

        # start server to server communication engine
        # --TODO-- implement server to server communication classes
        # self.server_state_duplication_worker = ServerStateDuplicator(T, SERVER_ID, port_number=8383)
        # self.server_state_duplication_worker.start()

        # start client facing game state publisher
        self.publisher_worker = GameStatePublisher(self.T, port_number=8181)
        self.publisher_worker.start()

        # start client commands worker
        self.client_command_worker = ClientCommandManager(self.T, self.clients_cmds_box, port_number=8282)
        self.client_command_worker.start()

    def mainloop(self):
        while self.T.is_game_running():
            # just sleep for 500ms while waiting the game to end
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
