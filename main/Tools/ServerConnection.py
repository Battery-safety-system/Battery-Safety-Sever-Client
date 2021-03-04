#!/usr/bin/python3
import time
import can

import cantools
import os
import csv
import socket
import pickle

class Connection(object):

    def __init__(self):

        self.ip_addr='192.168.137.1'
        self.ip_port = 6699
        self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    def reconnect(self):
        self.connect.close();
        self.connect, (host, port) = self.server.accept()
        print(u'the client %s:%s has connected.' % (host, port))

    def connect(self):

        self.server.bind((self.ip_addr, self.ip_port))
        self.server.listen(5)
        print(u'waiting for connect...')
        self.connect, (host, port) = self.server.accept()
        print(u'the client %s:%s has connected.' % (host, port))

    def receiveContent(self):
        self.connect.settimeout(15)
        content = pickle.loads(self.connect.recv(9216));
        return content;


        

