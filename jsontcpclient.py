#!/usr/bin/python
# -*- coding: utf-8 -*-

__author__ = "Abiezer Reyes"
__email__ = "reyes.abiezer@gmail.com"
__version__ = '0.1.1'


import logging
import struct

import simplejson
import tornado.gen
import tornado.ioloop
import tornado.iostream
import tornado.options
import tornado.tcpclient


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

    def __init__(self, address, port):
        self._stream = None
        self._address = address
        self._port = port
        self._packet = tcpclass()
        self.data = None
        self.id = None

    @tornado.gen.coroutine
    def connect(self):
        try:
            logging.info("Connecting to {0}:{1}...".format(self._address, self._port))
            stream = tornado.tcpclient.TCPClient()
            self._stream = yield stream.connect(self._address, self._port)
            self._stream.set_close_callback(self.on_close)
            tornado.ioloop.IOLoop.current().spawn_callback(self.read)
        except Exception as err:
            logging.error("TCP_ClientConnection {0} connect Error: {1}".format(self._address, err))
            yield tornado.gen.sleep(5)
            tornado.ioloop.IOLoop.current().add_callback(self.connect)
            pass

    @tornado.gen.coroutine
    def on_close(self):
        logging.warning("{} client disconnected!".format(self._address))
        yield tornado.gen.sleep(5)
        tornado.ioloop.IOLoop.current().add_callback(self.connect)

    @tornado.gen.coroutine
    def write(self, msg):
        try:
            # Encapsulate message and send
            yield self._stream.write(self._packet.Pack(simplejson.dumps(msg)))
        except tornado.iostream.StreamClosedError as err:
            logging.error("TCP_ClientConnection write Error: {} disconnected?".format(self._address))
            yield tornado.gen.sleep(5)
            tornado.ioloop.IOLoop.current().add_callback(self.connect)
            pass

    @tornado.gen.coroutine
    def read(self):
        try:
            while True:
                # Read the first 4 bytes to get the encapsulated message lenght
                header = yield self._stream.read_bytes(4)
                print header
                # Then, read the exact ammount of bytes containing the json data
                data = yield self._stream.read_bytes(self._packet.Unpack(header))
                print data
                self.data = simplejson.loads(data)
                # Do what you want with the data received
                yield self.processData()
                yield tornado.gen.sleep(0.25)
        except tornado.iostream.StreamClosedError as err:
            logging.error(
                "TCP_ClientConnection read Error: {} disconnected?".format(self._address))
            yield tornado.gen.sleep(5)
            tornado.ioloop.IOLoop.current().add_callback(self.connect)
            pass

    @tornado.gen.coroutine
    def processData(self):
        logging.info("Received from {0}: {1}".format(self._address, self.data))


if __name__ == '__main__':
    tornado.options.define("port", default=5000,
                           help="Run on the given port", type=int)
    tornado.options.define("address", default='127.0.0.1',
                           help="Connect to address", type=str)
    tornado.options.parse_command_line()
    tornado.options.options.logging = 'info'

    try:
        io = tornado.ioloop.IOLoop().current()
        tcpClient = TCP_ClientConnection(address=tornado.options.options.address, port=tornado.options.options.port)
        io.add_callback(tcpClient.connect)
    except Exception as err:
        logging.error("Error: {}".format(err))
        pass
    io.start()
