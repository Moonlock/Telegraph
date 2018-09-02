from symbols import Symbol
from subprocess import call
import signal
import socket
import sys


TIME_UNIT = 0.1

def signal_handler(sig, frame):
    print("Shutting down server.")
    s.close()
    sys.exit()

def handleMessage(msg):
    sonicPiCode = ""
    for byte in msg:
        symbols = parseSymbols(byte)
        while symbols:
            symbol = symbols.pop()
            if symbol == Symbol.DIT:
                sonicPiCode = addSymbolToCode(sonicPiCode, TIME_UNIT)
            elif symbol == Symbol.DAH:
                sonicPiCode = addSymbolToCode(sonicPiCode, 3*TIME_UNIT)
            elif symbol == Symbol.CHAR_SPACE:
                sonicPiCode = addSymbolToCode(sonicPiCode, 0, 2*TIME_UNIT)
            elif symbol == Symbol.WORD_SPACE:
                sonicPiCode = addSymbolToCode(sonicPiCode, 0, 6*TIME_UNIT)
    call(["sonic_pi", sonicPiCode])

def parseSymbols(byte):
    symbols = []
    for i in range(4):
        symbols.append((byte >> i*2) & 0x3)
    return symbols

def addSymbolToCode(code, duration, sleep=TIME_UNIT):
    code += "play 80, release: " + str(duration) + ";" if duration else ""
    code += "sleep " + str(sleep) + ";"
    return code

def run(port):
    signal.signal(signal.SIGINT, signal_handler)

    try:
        global s
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        s.bind(('', int(port)))
    except socket.error as e:
        print("Failed to create socket.  {}: {}".format(e.errno, e.strerror))
        sys.exit()

    s.listen(10)

    while True:
        conn, addr = s.accept()
        data = conn.recv(1024)
        conn.close()
        handleMessage(data)

