#!/usr/bin/python
from common.settings import *

import sys
from client.GUIDisplay import GUIDisplay

if AWS_MODE_FLAG:
    servers_list = SERVERS_AWS_PUBLIC
else:
    servers_list = SERVERS_LOCAL

idx = 0

if len(sys.argv) == 2:
    idx = int(sys.argv[1])

print "Starting viewer from %s.." % servers_list[idx]["server_id"]
print servers_list[idx]["server2client"]

guidisplay = GUIDisplay(servers_list[idx]["server2client"], with_background=True)
guidisplay.mainloop()
