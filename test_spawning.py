import zmq
import uuid
from random import randint

context = zmq.Context()
server_file = "server.txt"
servers = []

with open(server_file) as f:
    next(f)
    for line in f:
        server_adresses = line.strip().split(",")
        servers.append({
            "client2server": server_adresses[0],
            "server2client": server_adresses[1],
            "server2server": server_adresses[2]
        })

connections = []

for server in servers:
    socket = context.socket(zmq.REQ)
    socket.connect("tcp://" + server["client2server"])
    connections.append(socket)

for i in range(600):
    rand_server = randint(0, len(connections) - 1)
    socket = connections[rand_server]

    socket.send_json({
            "type" : "spawn",
            "player_id" : uuid.uuid4().hex,
            "player_type" : "human"
        })
    response = socket.recv()

for socket in connections:
    socket.close()