#!/usr/bin/python3
import time
import can
import RPi.GPIO as GPIO
import cantools
import os
import csv
import socket
import pickle

class Connection(object):

	    """docstring for PCConnection"""
    def __init__(self):
        super(PCConnection, self).__init__()
        self.ip_addre='192.168.137.1'
        self.ip_port = 6699
        self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    def connect(self):
        self.server.bind((self.ip_addr, self.ip_port))
        self.server.listen(5)
        print(u'waiting for connect...')
        self.connect, (host, port) = self.server.accept()
        print(u'the client %s:%s has connected.' % (host, port))

    def receiveContent(self, keyWords):
    	self.connect.settimeout(60)
    	try: 
        	content = pickle.loads(self.connect.recv(9216));
        except Exception as e:
        	raise Exception(keyWords + "receiving error")
        return content;


        

