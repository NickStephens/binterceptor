#!/usr/bin/python

import socket
import converter
import time
import os
import subprocess
import signal
import errno

# GLOBAL SOCKET DESCRIPTORS
client = None
server = None

def main():
    global client
    global server

    # read from config and get port
    # if not set default to 13074
    sockfd = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sockfd.bind(("0.0.0.0", 13074))
    sockfd.listen(1)
    client, desc = sockfd.accept()
    print "Incoming connection from", desc 

    # read from config and get forward
    # target and port
    server = socket.create_connection(("www.google.com", 80)) 

    interceptionLoop(client, server)

def interceptionLoop(clientSock, serverSock):
    """ the BINTERCEPTOR's dark heart """
    signal.signal(signal.SIGINT, close)
    while True:
        cdata = handledRecv(clientSock, 2048)
        if (not cdata): break

        # if dropped, wait for more client data
        if (not prompt(cdata, serverSock, "client")):
            continue

        sdata = handledRecv(serverSock, 2048)
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
        print "dropped" 
        return False 
    elif (decision == "Q"):
        close(None, None)
    else:
        forward(data, targetSock)

    return True

def forward(data, targetSock):
    print "forwarded"
    targetSock.send(data)

def edit(data, targetSock, targetName):
    """ opens up user's editor and allows them edit the payload in 'pretty hex' 
    syntax  """

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
            
def close(sig, stackframe):
    print "closing ..."
    client.close()    
    server.close()
    exit(1)

main()
