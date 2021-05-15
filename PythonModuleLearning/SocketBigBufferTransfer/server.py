#!/usr/bin/python3
import time
import os
import csv
import socket
import pickle
import json
import sys;
import regex;
server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
# ip_port = 6699
# ip_addr = "192.168.137.1"
ip_port = 9090
ip_addr = "localhost"

server.bind((ip_addr, ip_port))
server.listen(5)
print(u'waiting for connect...')
connect, (host, port) = server.accept()
print(u'the client %s:%s has connected.' % (host, port))
content = connect.recv(1024 * 7).decode('utf-8')
# print(type(content_part.decode('utf-8')))
# content = json.loads(content_part.decode('utf-8'))
# # self.content = pickle.loads(orig_content)
# print("content : " + str(content))
#
# content.split()
if ('{' in content and '}' in content):
    index1 = content.find('{');
    index2 = content.find('}')
print(type(content))

