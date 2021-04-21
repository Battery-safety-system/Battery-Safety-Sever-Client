#!/usr/bin/python3
import time
import os
import csv
import socket
import pickle
import json
import sys;
server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
ip_port = 6699
ip_addr = "192.168.137.1"

server.bind((ip_addr, ip_port))
server.listen(5)
print(u'waiting for connect...')
connect, (host, port) = server.accept()
print(u'the client %s:%s has connected.' % (host, port))
# orig_content = connect.recv(1024 * 1024 * 1024 * 10)
# # print(orig_content.decode('utf-8'))
# # content = json.loads(orig_content.decode('utf-8'))
# # content = pickle.loads(orig_content)
# print(sys.getsizeof(orig_content))
# print(orig_content)

# orig_content2 = connect.recv(1024 * 9)
orig_content_part1 = connect.recv(1024 * 9)
orig_content_part2 = connect.recv(1024 * 9)
orig_content = orig_content_part1 + orig_content_part2
print(orig_content)
orig_str = orig_content.decode('utf-8')
# print(orig_str)
content = json.loads(orig_str)
# # self.content = pickle.loads(orig_content)
print("content : " + str(content))

