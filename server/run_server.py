import sys
from server.Server import Server

server_id = 1
verbose = False

if len(sys.argv) == 2:
    server_id = int(sys.argv[1])

print "Starting Dragons Arena server %d.." % server_id

S = Server(server_id=server_id, verbose=verbose)

# go into main loop
S.mainloop()

print "Server process exits.."
