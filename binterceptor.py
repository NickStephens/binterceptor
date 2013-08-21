#!/usr/bin/python

import getopt
import socket
import converter
import time
import os
import sys
import subprocess
import signal
import errno

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
        opts, args = getopt.getopt(sys.argv[1:], "l:f:p:h", ["listen=",
        "forward-host=","forward-port=", "help"])
    except getopt.GetoptError as err:
        print str(err) 
        usage()
        sys.exit(1)
    for o, a in opts:
        if o in ("-l", "--listen"):
            lport = a
        elif o in ("-f", "--forward-host"):
            rhost = a
        elif o in ("-p", "--forward-port"):
            rport = a
        elif o in ("-h", "--help"):
            usage()
            sys.exit(1)

    if rhost == None or rport == None:
        print "Forward host or forward port not set"
        usage()
        sys.exit(1)
            
    sockfd = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sockfd.bind(("0.0.0.0", int(lport)))
    sockfd.listen(1)
    client, desc = sockfd.accept()
    print "Incoming connection from", desc 

    server = socket.create_connection((rhost, int(rport))) 

    interceptionLoop(client, server)

def interceptionLoop(clientSock, serverSock):
    """ the BINTERCEPTOR's dark heart """
    signal.signal(signal.SIGINT, close)
    while True:
        # cdata = handledRecv(clientSock, 2048)
        cdata = clientSock.recv(2048)
        if (not cdata): break

        # if dropped, wait for more client data
        if (not prompt(cdata, serverSock, "client")):
            continue

        # sdata = handledRecv(serverSock, 2048)
        sdata = serverSock.recv(2048)
        if (not sdata): break
        prompt(sdata, clientSock, "server")

def prompt(data, targetSock, targetName):
    """ prompts user for a decision regarding the data captured returns False 
    if the data was dropped, True otherwise """

    print "[{}] want(s) to send ...".format(targetName)
    prettyhex = converter.convertFromRawPretty(data)
    print prettyhex

    decision = raw_input("edit, forward, drop, or quit? [F/e/d/q] ").upper()

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
    editor = os.environ['EDITOR']
    if (not editor):
        editor = "nano" 
    subprocess.call([editor, filename], shell=False)

    # convert file to binary and prompt new data
    file = open(filename, "r")
    newdata = converter.convertToRaw(file.read())
    file.close()
    os.remove(filename)
    prompt(newdata, targetSock, "you as " + targetName)

def handledRecv(targetSock, buf):
    try:
        data = targetSock.recv(buf)
    except socket.error as (code, msg):
        if code != errno.EINTR:
            raise
        else: 
            close(None, None)
    return data

def usage():
    print """
    usage: binterceptor -l [listenport] -f [forwardhost] -p [forwardport]
    
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
    sys.exit(2)

if __name__ == "__main__":
    main()
