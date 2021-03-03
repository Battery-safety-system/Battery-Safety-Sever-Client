#!/usr/bin/python3
import time
import can
import RPi.GPIO as GPIO
import cantools
import os
import csv
import socket
import pickle


class PCConnection(object):
    """docstring for PCConnection"""
    def __init__(self):
        super(PCConnection, self).__init__()
        self.ip_addre='192.168.137.1'
        self.ip_port = 6699

    def connect(self):
        self.client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.client.connect((self.ip_addre, self.ip_port))
        print('socket has connected')

    
    def sendContent(self, keyword, list_sent):
        dict_exp = {}
        dict_exp["keyword"] = keyword;
        dict_exp["list"] = list_sent;
        dict_pickle = pickle.dumps(dict_exp);
        self.client.settimeout(15)
        try:
            self.client.send(dict_pickle)
        except Exception as e:
            raise Exception("sendContent: " + str(keyword) + " Error");

    


        