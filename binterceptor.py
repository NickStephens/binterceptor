#!/usr/bin/python

import socket
import converter
import time
import os

def main():

    # read from config and get port
    # if not set default to 13074
    sockfd = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sockfd.bind(("0.0.0.0", 13074))
    sockfd.listen(1)
    client, desc = sockfd.accept()
    print "Incoming clientection from", desc 

    # read from config and get forward
    # target and port
    server = socket.create_connection(("www.google.com", 80)) 
    interceptionLoop(client, server)

def interceptionLoop(clientSock, serverSock):
    """ the BINTERCEPTOR's dark heart """
    while True:
        cdata = clientSock.recv(2048)
        if (not cdata): break
        # edit, forward, or drop? [F/e/d] 
        if (not prompt(cdata, serverSock, "client")):
            continue
        # send to server if forwarded is selected
        sdata = serverSock.recv(2048)
        if (not sdata): break
        prompt(sdata, clientSock, "server")
        # edit, forward, or drop?

def prompt(data, targetSock, targetName):
    """ prompts user for a decision regarding the data captured returns False 
    if the data was dropped, True otherwise """

    print "[{}] sending ...".format(targetName)
    prettyhex = converter.convertFromRawPretty(data)
    print prettyhex

    decision = raw_input("edit, forward, or drop? [F/e/d] ").upper()

    if (decision == "F"):
        forward(data, targetSock)
    elif (decision == "E"):
        edit(data, targetSock, targetName)
    elif (decision == "D"):
        print "dropped" 
        return False 
    else:
        forward(targetSock, data)

    return True

def forward(data, targetSock):
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
    if (os.environ['EDITOR'])
    os.system("$EDITOR " + filename) #REALLY DANGEROUS!!! ONLY TESTING!!!
    # convert file to binary and prompt new data
    file = open(filename, "r")
    newdata = converter.convertToRaw(file.read())
    prompt(newdata, targetSock, "you")

main()
