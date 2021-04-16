#!/usr/bin/python3
import time

import os
import csv
import socket
import pickle
import json
import sys;
server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
ip_port = 9090
ip_addr = 'localhost'

server.bind((ip_addr, ip_port))
server.listen(5)
print(u'waiting for connect...')
connect, (host, port) = server.accept()
print(u'the client %s:%s has connected.' % (host, port))
orig_content = connect.recv(1024 * 1024 * 20)
# content = json.loads(orig_content.decode('utf-8'))
content = pickle.loads(orig_content)
print(content)

