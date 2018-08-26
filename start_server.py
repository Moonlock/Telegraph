#! /usr/bin/python3

import server
import sys

DEFAULT_PORT = 8000

port = sys.argv[1] if len(sys.argv) > 1 else DEFAULT_PORT
server.run(port)
