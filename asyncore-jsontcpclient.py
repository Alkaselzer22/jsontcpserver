#!/usr/bin/python
# -*- coding: utf-8 -*-

__author__ = "Abiezer Reyes"
__email__ = "reyes.abiezer@gmail.com"
__version__ = '0.1.1'


import asyncore
import logging
import socket
import struct

import simplejson
import tornado.options

# Empty dictionary to pass it to asyncore.
# This is used by asyncore to interact between threads
threadMap = {}


# Class for TCP Packet Encapsulation
class tcpclass:
    def __init__(self, delimiter='<i'):
        self.tcpstruct = struct.Struct(delimiter)
    # Encapsulates json data's lenght and the data in the same message

    def Pack(self, msg):
        return self.tcpstruct.pack(len(str(msg))) + str(msg)
    # Get incomming json data's lenght

    def Unpack(self, msg):
        return self.tcpstruct.unpack(msg)[0]


# TCP Client class for Server connections
class TCP_ClientConnection(asyncore.dispatcher):
    def __init__(self, address, port):
        global threadMap
        asyncore.dispatcher.__init__(self, map=threadMap)
        self.server_address = address
        self.server_port = port
        self._packet = tcpclass()
        self.data = None
        self.id = None
        logging.info("Connecting to {0}:{1}...".format(self.server_address, self.server_port))
        self.create_socket(socket.AF_INET, socket.SOCK_STREAM)
        self.connect((self.server_address, self.server_port))

    def handle_connect(self):
        logging.info("Connected to {0}:{1}...".format(self.server_address, self.server_port))

    def handle_close(self):
        logging.warning("{0}:{1} client connection closed.".format(self.server_address, self.server_port))
        self.close()

    def writable(self):
        if self.toServer and len(self.toServer) > 0:
            return True
        else:
            return False

    def readable(self):
        return True

    def handle_write(self):
        logging.info('Sending to {0}:{1} {2}'.format(self.server_address, self.server_port, self.toServer))
        self.send(self._packet.Pack(simplejson.dumps(self.toServer, encoding='latin-1')))
        self.toServer = None

    def handle_read(self):
        # Read the first 4 bytes to get the encapsulated message lenght
        header = self.recv(4)
        # Then, read the exact ammount of bytes containing the json data
        data = self.recv(self._packet.Unpack(header))
        self.data = simplejson.loads(data)
        # Do what you want with the data received
        self.processData()

    def processData(self):
        logging.info("Received from {0}:{1} {2}".format(self.server_address, self.server_port, self.data))


if __name__ == '__main__':
    tornado.options.options.logging = 'info'
    tornado.options.parse_command_line()
    tcpClient = TCP_ClientConnection(address=tornado.options.options.address, port=tornado.options.options.port)

    asyncore.loop(map=threadMap)
