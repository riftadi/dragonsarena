#!/usr/bin/python
import time
from client.ClientThread import ClientThread as Client
from common.settings import *

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
for command in trace:
    print "COMMAND %d from %d" % (current, total)
    current = current + 1

    execution = (GTA_DURATION * command["time"])
    uid = command["pid"]
    action = command["action"]

    time.sleep(execution - last)
    last = execution
    if action == "PLAYER_LOGIN":
        c = Client(uid)
        c.start()
        clients[uid] = c
    elif action == "PLAYER_LOGOUT":
        if clients.has_key(uid):
            c = clients.get(uid)
            c.set_offline()
            # JOINING TAKES A LONG TIME WHEN SKIPPING WE HAVE A LOT OF DEAD THREADS BUT GAIN PERFORMANCE
            #c.join()

print "DONE"
