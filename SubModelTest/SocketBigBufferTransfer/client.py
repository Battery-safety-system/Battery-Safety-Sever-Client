#!/usr/bin/python3
import time
import json
import socket
import pickle
import sys;
ip_addre = 'localhost'
ip_port = 9090
client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client.connect((ip_addre, ip_port))
dict1 = {}
filename = "log-Battery-System.csv"
with open(filename) as f:
    s = f.readline() + '\n' # add trailing new line character
    labels = s.split(',');
    content = "first";
    index = 0;
    while True:
        content = f.readline()
        if not content:
            break;
        content_list = content.split(',')
        for i in range(len(labels)):
            dict1[labels[i] + str(index)] = content_list[i]
        index = index + 1
    # print("new label: " + str(labels))

print(dict1)
# dict1repr(s) =
list1 = [ dict1 for i in range(10)]
content = pickle.dumps(list1);

# # content = json.dumps(dict1).encode('utf-8')
client.send(content)