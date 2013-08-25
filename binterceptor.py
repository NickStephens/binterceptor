#!/usr/bin/python

import getopt
import socket
import converter
import time
import os
import subprocess
import signal
import errno
from sys import argv, exit

# GLOBAL SOCKET DESCRIPTORS
client = None
server = None

def main():
    global client
    global server

    rhost = None
    rport = None
    lport = "13074"

    try:
        opts, args = getopt.getopt(argv[1:], "l:h", ["listen=",
        "help"])
    except getopt.GetoptError as err:
        print str(err) 
        usage()
        exit(1)
    for o, a in opts:
        if o in ("-l", "--listen"):
            lport = a
        elif o in ("-h", "--help"):
            usage()
            exit(1)

    if len (opts) == 0 and len(argv) == 4:
        rhost = argv[2]
        rport = argv[3]
    elif len(argv) == 5:
        rhost = argv[3]
        rport = argv[4]

    if rhost == None or rport == None:
        print "Forward host or forward port not set"
        usage()
        exit(1)
            
    sockfd = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sockfd.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    sockfd.bind(("0.0.0.0", int(lport)))
    sockfd.listen(1)
    client, desc = sockfd.accept()
    print "Incoming connection from", desc 

    server = socket.create_connection((rhost, int(rport))) 
    server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

    interceptionLoop(client, server)

def interceptionLoop(clientSock, serverSock):
    """ the BINTERCEPTOR's dark heart """
    signal.signal(signal.SIGINT, close)
    while True:
        # cdata = handledRecv(clientSock, 2048)
        if (promptListen()):
            cdata = clientSock.recv(2048)
            if (not cdata): break

        # if dropped, wait for more client data
            promptAction(cdata, serverSock, "client")
            if (promptListen()):
                continue

        # sdata = handledRecv(serverSock, 2048)
        sdata = serverSock.recv(2048)
        if (not sdata): break
        promptAction(sdata, clientSock, "server")

def promptListen():
    """ prompts the user to decide which host to listen for returns False for server"""
    decision = raw_input("listen for client or server? [C/s] ").upper()
    if (decision == "C"):
        return True
    elif (decision == "S"):
        return False
    return True

def promptAction(data, targetSock, targetName):
    """ prompts user for a decision regarding the data captured returns False 
    if the data was dropped, True otherwise """

    print "[{}] want(s) to send ...".format(targetName)
    prettyhex = converter.convertFromRawPretty(data)
    print prettyhex

    decision = raw_input("forward, edit, drop, or quit? [F/e/d/q] ").upper()

    if (decision == "F"):
        forward(data, targetSock)
    elif (decision == "E"):
        edit(data, targetSock, targetName)
    elif (decision == "D"):
        print "\033[0;31mdropped\033[0m" 
        return False 
    elif (decision == "Q"):
        close(None, None)
    else:
        forward(data, targetSock)

    return True

def forward(data, targetSock):
    print "\033[0;32mforwarded\033[0m"
    targetSock.send(data)

def edit(data, targetSock, targetName):
    """ opens up user's editor and allows them edit the payload in 'pretty hex' 
    syntax  """

    print "\033[0;33mediting\033[0m"
    # write contents to a temporary file in tmp"
    filename = "binterceptor-" + str(time.time())
    file = open(filename, "w")
    file.write(converter.convertFromRaw(data))
    file.close()

    # open up $EDITOR on that file
    try:
        editor = os.environ['EDITOR']
    except:
        editor = "vi" 
    subprocess.call([editor, filename], shell=False)

    # convert file to binary and prompt new data
    file = open(filename, "r")
    try:
        newdata = converter.convertToRaw(file.read())
    except:
        print "bad hexadecimal values written, reverting to old data ..."
        file.close()
        os.remove(filename)
        promptAction(data, targetSock, targetName)
    file.close()
    os.remove(filename)
    promptAction(newdata, targetSock, "you as " + targetName)

def usage():
    print """
    usage: binterceptor [-l listenport] FORWARDHOST FORWARDPORT
    
    options:
    -h, --help          print this message
    -l, --listen        port to listen on
    -f, --forward-host  host to forward data to 
    -p, --forward-port  port to forward data to 
    """
    
def close(sig, stackframe):
    print "closing ..."
    client.close()    
    server.close()
    exit(2)

if __name__ == "__main__":
    main()
