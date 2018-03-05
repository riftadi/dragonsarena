import time
import zmq
import json
from TSSEngine import TSSEngine
from UnifiedMessageBox import UnifiedMessageBox

context = zmq.Context()
socket = context.socket(zmq.REP)
socket.bind("tcp://127.0.0.1:5555")

msg_box = UnifiedMessageBox(True)
game_engine =  TSSEngine(25, 25, msg_box)
game_engine.start()

# process commands of connected clients
while True:
    #  Wait for next request from client
    json_message = socket.recv()

    parsed_message = json.loads(json_message)
    parsed_message["timestamp"] = game_engine.get_current_time()
    msg_box.put_message(parsed_message)

    #  Send reply back to client
    socket.send(b"ok")