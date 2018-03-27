#!/usr/bin/python
import sys
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
next_time = 0.0
context = zmq.Context()

# running clients
for idx in xrange(total):
    command = trace[idx]

    uid = command["pid"]
    action = command["action"]

    print "COMMAND %d from %d: p%s %s" % (idx+1, total, uid, action[7:].lower())

    if action == "PLAYER_LOGIN":
        c = Client(uid, context)
        c.start()
        clients[uid] = c
    elif action == "PLAYER_LOGOUT":
        if clients.has_key(uid):
            c = clients.get(uid)
            c.set_offline()
            # JOINING TAKES A LONG TIME WHEN SKIPPING WE HAVE A LOT OF DEAD THREADS BUT GAIN PERFORMANCE
            # c.join()
            clients.pop(uid, None)

    if idx < (total-1):
        sleep_delay = float(GTA_DURATION * (float(trace[idx+1]["time"]-float(trace[idx]["time"]))))
        time.sleep(sleep_delay)    

print "wait for clients to finish.."

for uid in clients:
    c = clients.get(uid)
    c.join()

context.term()

print "DONE"

