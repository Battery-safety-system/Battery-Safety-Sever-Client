#!/usr/bin/python3
import time
import os
import csv
import pickle
import socket
import logging
from File import File
from Connection import Connection

class Server_PC:
    def __init__(self):
        ## section1: file and floder creation
        self.FileObj = new File();
        self.ConnectionObj = new Connection();
        self.DataHandlerObj = new DataHandler();

    def run(self):

        self.Connection.connect();
        content = self.Connection.receiveContent();
        labels = self.DataHandlerObj.getLabelFromDict(content);
        while True:
            print('start the loop')
            try: 
                content = self.Connection.receiveContent("data");
                datas = self.DataHandlerObj.getDataFromDict(content);

                content = self.Connection.receiveContent("status");
                status = self.DataHandlerObj.getStatusFromDict(content);
            except Exception as e:
                print(e)
                self.Connection.reconnect();

            print(self.DataHandler.getDeviceInfoString(status))
            print(self.DataHandler.getStatusInfoString(status))
            self.FileObj.WritetoCVS(datas, labels);
            print('end the loop \n')


server_PC = Server_PC();
server_PC.run();
                    
                

