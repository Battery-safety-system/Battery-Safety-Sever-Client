#!/usr/bin/python3
import time

import os
import csv
import socket
import pickle
import json
import sys
import re;

class Connection(object):

    def __init__(self):
        with open('config.properties') as f:
            data = json.load(f)
        self.ip_port = int(data["ip_port"])
        self.ip_addr = data["ip_addr"]
        self.content = {};
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
        if(self.LoopIfNotMeetReq(self.receiveContentFromClient, 3)):
            return self.content;
        else:
            raise Exception("ServerConnection_receiveContent: Error!!! cannot receiveContent in ServerConnection")



    def LoopIfNotMeetReq(self, handler1, times, *args, **kwargs):

        for i in range(times):
            if (handler1(*args)):
                return True;
        return False;
        
    def receiveContentFromClient(self):
        orig_content = "";
        for i in range(3):
            try:
                self.connect.settimeout(20)
                content_part = self.connect.recv(1024 * 7).decode('utf-8');
            except Exception as e:
                print("ServerConnection: receiveContentFromClient: " + e)
                return False
            orig_content += content_part;
            if re.search("\{(.+)\}", orig_content):
                content = re.findall("\{(.+)\}", orig_content)[0]
                content = "{" + content + "}"
                self.content = json.loads(content)
                return True;
        return False;
