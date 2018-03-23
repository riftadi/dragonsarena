import zmq
import uuid
from random import randint
from common.settings import *


context = zmq.Context()
servers = SERVERS_LOCAL
connections = []

for i in xrange(N_SERVERS):
    socket = context.socket(zmq.REQ)
    socket.connect("tcp://" + servers[i]["client2server"])
    connections.append(socket)

for i in range(600):
    rand_server = randint(0, len(connections) - 1)
    socket = connections[rand_server]

    socket.send_json({
            "type" : "spawn",
            "player_id" : uuid.uuid4().hex,
            "player_type" : "h"
        })
    response = socket.recv()

for socket in connections:
    socket.close()