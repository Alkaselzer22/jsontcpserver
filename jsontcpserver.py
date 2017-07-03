#!/usr/bin/python
# -*- coding: utf-8 -*-

__author__ = "Abiezer Reyes"
__email__ = "reyes.abiezer@gmail.com"
__version__='0.1.1'


import logging
import struct

import simplejson
import tornado.gen
import tornado.ioloop
import tornado.iostream
import tornado.options
import tornado.tcpserver


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
class TCP_ClientConnection(object):
    clients = set()
    def __init__(self, stream, address):
        self._stream = stream
        self._address = address
        self._stream.set_close_callback(self.close)
        self._packet = tcpclass()
        self.data = None
        # Fire up the reading
        tornado.ioloop.IOLoop.current().spawn_callback(self.read)

    @tornado.gen.coroutine
    def close(self):
        logging.warning("{} client disconnected!".format(self._address))
        TCP_Server.removeClient(self)
    @tornado.gen.coroutine
    def write(self, msg):
        try:
            # Encapsulate message and send
            yield self._stream.write(self._packet.Pack(msg))
        except tornado.iostream.StreamClosedError as err:
            logging.error("TCP_ClientConnection write Error: {} disconnected?".format(self._address))
            TCP_Server.removeClient(self)

    @tornado.gen.coroutine
    def read(self):
        try:
            while True:
                # Read the first 4 bytes to get the encapsulated message lenght
                header = yield self._stream.read_bytes(4)
                # Then, read the exact ammount of bytes containing the json data
                data = yield self._stream.read_bytes(self._packet.Unpack(header))
                self.data = simplejson.loads(data)
                # Do what you want with the data received
                yield self.processData()
                yield tornado.gen.sleep(0.25)
        except tornado.iostream.StreamClosedError as err:
            logging.error("TCP_ClientConnection read Error: {} disconnected?".format(self._address))
            TCP_Server.removeClient(self)

    @tornado.gen.coroutine
    def processData(self):
        logging.info("Received from {0}: {1}".format(self._address, self.data))


# Async TCP Server
class TCP_Server(tornado.tcpserver.TCPServer):
    clients = {}

    @classmethod
    @tornado.gen.coroutine
    def addClient(self, client):
        self.clients[client.id] = client

    @classmethod
    @tornado.gen.coroutine
    def removeClient(self, client):
        del self.client[client.id]

    @classmethod
    @tornado.gen.coroutine
    def toClient(self, clientID, msg):
        yield self.clients[clientID].write(msg)

    # Create a new TCP_ClientConnection instance for each connection
    @tornado.gen.coroutine
    def handle_stream(self, stream, address):
        TCP_ClientConnection(stream, address)
        logging.info("Client proccess connected: {}".format(address))


if __name__ == '__main__':
    # Parse commands so logging fires up
    tornado.options.parse_command_line()
    tornado.options.options.logging = 'info'

    # Init Server
    server = TCP_Server()
    server.listen(5000)

    # Fire up tornado's ioloop
    tornado.ioloop.IOLoop.current().start()
