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

        self.peers = {
                        1 : {"client2server" : {"host" : "127.0.0.1", "port" : "8282"},
                            "server2client" : {"host" : "127.0.0.1", "port" : "8181"},
                            "server2server" : {"host" : "127.0.0.1", "port" : "8383"},},

                        2 : {"client2server" : {"host" : "127.0.0.1", "port" : "9292"},
                            "server2client" : {"host" : "127.0.0.1", "port" : "9191"},
                            "server2server" : {"host" : "127.0.0.1", "port" : "9393"},},

                        3 : {"client2server" : {"host" : "127.0.0.1", "port" : "8282"},
                            "server2client" : {"host" : "127.0.0.1", "port" : "8181"},
                            "server2server" : {"host" : "127.0.0.1", "port" : "8383"},},

                        4 : {"client2server" : {"host" : "127.0.0.1", "port" : "8282"},
                            "server2client" : {"host" : "127.0.0.1", "port" : "8181"},
                            "server2server" : {"host" : "127.0.0.1", "port" : "8383"},},

                        5 : {"client2server" : {"host" : "127.0.0.1", "port" : "8282"},
                            "server2client" : {"host" : "127.0.0.1", "port" : "8181"},
                            "server2server" : {"host" : "127.0.0.1", "port" : "8383"},}
                    }

        # temporary hack to develop within one machine
        self.peer_id = 0

        if self.server_id == 1:
            self.peer_id = 2
        elif self.server_id == 2:
            self.peer_id = 1

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
        self.publisher_worker = GameStatePublisher(self.T, self.zmq_root_context, port_number=self.peers[self.peer_id]["server2client"]["port"])
        self.publisher_worker.start()

        # start server to server communication engine
        self.server_cmd_duplicator_worker = ServerCommandDuplicator(self.T, self.zmq_root_context, self.clients_cmds_box,
                    self.server_id, port_number=self.peers[self.peer_id]["server2server"]["port"])
        self.server_cmd_duplicator_worker.start()
        self.server_cmd_duplicator_worker.create_game_start_message(self.absolute_game_start_time)

        # start client commands worker
        self.client_command_worker = ClientCommandManager(self.T, self.zmq_root_context, self.server_id, self.clients_cmds_box,
            self.server_cmd_duplicator_worker, port_number=self.peers[self.peer_id]["client2server"]["port"])
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
