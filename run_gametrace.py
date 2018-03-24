#!/usr/bin/python
import time
from client.ClientThread import ClientThread as Client
from common.settings import *

import zmq

gametrace = "game_trace.csv"
clients = {}
trace = []

with open(gametrace) as f:
    next(f)
    for line in f:
        command = line.strip().split(",")
        trace.append({
            "pid": command[0],
            "time": float(command[1]),
            "action": command[2]
})

total = len(trace)
current = 1
last = 0
zmq_root_context = zmq.Context()

# running clients
for command in trace:
    current = current + 1

    execution = (GTA_DURATION * command["time"])
    uid = command["pid"]
    action = command["action"]

    print "COMMAND %d from %d: p%s %s" % (current, total, uid, action[7:].lower())

    time.sleep(execution - last)
    last = execution

    if action == "PLAYER_LOGIN":
        c = Client(uid, zmq_root_context)
        c.start()
        clients[uid] = c
    elif action == "PLAYER_LOGOUT":
        if clients.has_key(uid):
            c = clients.get(uid)
            c.set_offline()
            # JOINING TAKES A LONG TIME WHEN SKIPPING WE HAVE A LOT OF DEAD THREADS BUT GAIN PERFORMANCE
            c.join()
            clients.pop(uid, None)

for uid in clients:
    c = clients.get(uid)
    c.join()

zmq_root_context.term()

print "DONE"

