#!/usr/bin/python3
import time
import can
import cantools
import os
import csv
import socket
import pickle


class PCConnection(object):
    """docstring for PCConnection"""

    def __init__(self):
        # super(PCConnection, self).__init__()
        self.ip_addre = '192.168.137.1'
        self.ip_port = 6699
        self.errorTimes = 0;
        self.isError = False;
        self.recurTimes = 20;

    def connect(self):

        self.client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.client.connect((self.ip_addre, self.ip_port))


    def sendContent(self, dictContent):
        if(self.isError == True and self.errorTimes < self.recurTimes):
            self.errorTimes += 1;
            print("Try to reconnect after " + str(self.recurTimes - self.errorTimes))
            return ;
        dict_pickle = pickle.dumps(dictContent);
        self.client.settimeout(5)
        try:
            self.client.send(dict_pickle)
        except Exception as e:
            raise Exception("sendContent: Error");

    def close(self):
        # print("PC Connection close")
        self.client.close();

    def reconnectAfterLoops(self):
        self.isError = True;
        if(self.errorTimes >= self.recurTimes):
            self.client.close();
            self.errorTimes = 0
            self.client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            try:
                self.client.connect((self.ip_addre, self.ip_port))
                self.isError = False;
            except Exception as e:
                print("Reconnection failed")





