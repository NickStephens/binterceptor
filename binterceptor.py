#!/usr/bin/python

import socket
import converter

def main():

    # read from config and get port
    # if not set default to 13074
    
    sockfd = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sockfd.bind(("0.0.0.0", 13074))
    sockfd.listen(1)
    client, desc = sockfd.accept()

    # read from config and get forward
    # target and port

    server = socket.create_connection(("localhost", 80)) 

    print "Incoming clientection from", desc 
    while True:
        cdata = client.recv(2048)
        if (not cdata): break
        print "[client] sending ..."
        hex = converter.convert(cdata)
        print hex
        # edit, forward, or drop? [F/e/d] 
        server.send(cdata)
        
        # send to server if forwarded is selected
        sdata = server.recv(2048)
        if (not sdata): break
        print "[server] sending ..."
        hex = converter.convert(sdata)
        print hex
        # edit, forward, or drop?
        

main()
