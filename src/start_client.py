#! /usr/bin/python3

from client import client
import sys

DEFAULT_SERVER = "localhost"
DEFAULT_PORT = 8000

server = sys.argv[1] if len(sys.argv) > 1 else DEFAULT_SERVER
port = sys.argv[2] if len(sys.argv) > 2 else DEFAULT_PORT
client.run(server, port)
