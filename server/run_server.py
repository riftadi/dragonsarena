import sys
from server.Server import Server
from common.settings import *

if AWS_MODE_FLAG:
    servers = SERVERS_AWS_PRIVATE
else:
    servers = SERVERS_LOCAL
    
server_id = 1
verbose = False

if len(sys.argv) == 2:
    server_id = int(sys.argv[1])
else:
    print "usage: python -m server.run_server <server_id>"
    sys.exit()

peers = []
host = {}

# load the host and peers information
for i in xrange(N_SERVERS):
    if servers[i]["server_id"] == server_id:
        host = servers[i]
    else:
        peers.append(servers[i])

print "Starting Dragons Arena server %d.." % server_id

S = Server(server_id=server_id, host=host, peers=peers, verbose=verbose)

# go into main loop
S.mainloop()

print "Server process exits.."
