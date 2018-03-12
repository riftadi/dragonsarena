#!/usr/bin/python

import sys
from client.GUIDisplay import GUIDisplay

publisher_url = "127.0.0.1:9191"

if len(sys.argv) == 2:
    publisher_url = sys.argv[1]

print "Starting viewer from %s.." % publisher_url

guidisplay = GUIDisplay(publisher_url)
guidisplay.mainloop()
