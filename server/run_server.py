from server.Server import Server

SERVER_ID = 1
VERBOSE = False

print "Starting Dragons Arena server %d.." % SERVER_ID

S = Server(server_id=SERVER_ID, verbose=VERBOSE)

# go into main loop
S.mainloop()

print "Server process exits.."
