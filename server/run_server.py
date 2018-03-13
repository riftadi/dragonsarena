import sys
from server.Server import Server

server_id = 1
verbose = False

server_file = "server.txt"
peers = []
host = {}
current_line = 0

if len(sys.argv) == 2:
    server_id = int(sys.argv[1])

with open(server_file) as f:
    for line in f:
        if current_line == 0:
            current_line +=1
            continue
        servers = line.strip().split(",")
        if current_line == server_id:
            host["client2server"] = servers[0]
            host["server2client"] = servers[1]
            host["server2server"] = servers[2]
        else:
            peers.append({
                "client2server": servers[0],
                "server2client": servers[1],
                "server2server": servers[2]
            })
        current_line +=1

print "Starting Dragons Arena server %d.." % server_id

S = Server(server_id=server_id, host=host, peers=peers, verbose=verbose)

# go into main loop
S.mainloop()

print "Server process exits.."
