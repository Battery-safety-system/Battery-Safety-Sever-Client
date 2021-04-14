#!/usr/bin/python3
import time

import os
import csv
import socket
import pickle
import json

class Connection(object):

    def __init__(self):
        with open('config.properties') as f:
            data = json.load(f)
        self.ip_port = int(data["ip_port"])
        self.ip_addr = data["ip_addr"]
        #
        # self.ip_addr='192.168.137.1'
        # self.ip_port = 6699
        self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        self.connectToClient();
    def reconnect(self):
        self.connect.close();
        print(u'waiting for connect...')
        self.connect, (host, port) = self.server.accept()
        print(u'the client %s:%s has connected.' % (host, port))

    def connectToClient(self):

        self.server.bind((self.ip_addr, self.ip_port))
        self.server.listen(5)
        print(u'waiting for connect...')
        self.connect, (host, port) = self.server.accept()
        print(u'the client %s:%s has connected.' % (host, port))

    def receiveContent(self):
        self.connect.settimeout(40)
        content = pickle.loads(self.connect.recv(9216));
        # while True:
        #     try:
        #         content = pickle.loads(self.connect.recv(9216));
        #         break;
        #     except:
        #         continue


        return content;


        

