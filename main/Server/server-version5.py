#!/usr/bin/python3
import time
import os
import csv
import pickle
import socket
import logging
from File import File
from Connection import Connection
from DataHandler import DataHandler
from Connection import Connection


class Server_PC:
    def __init__(self):
        ## section1: file and floder creation
        self.FileObj = File();
        self.ConnectionObj = Connection();
        self.DataHandlerObj = DataHandler();

    def run(self):

        self.ConnectionObj.connect();
        content = self.ConnectionObj.receiveContent("labels");
        labels = self.DataHandlerObj.getLabelFromDict(content);
        datas = [];
        status = [];

        while True:
            print('start the loop')
            try:
                content = self.ConnectionObj.receiveContent("data");
                datas = self.DataHandlerObj.getDataFromDict(content);

                content = self.ConnectionObj.receiveContent("status");
                status = self.DataHandlerObj.getStatusFromDict(content);
            except Exception as e:
                print(e)
                self.ConnectionObj.reconnect();
                content = self.ConnectionObj.receiveContent("labels");
                labels = self.DataHandlerObj.getLabelFromDict(content);
                self.FileObj.updateWholeFile();
                continue;

            print(self.DataHandlerObj.getDeviceInfoString(status))
            print(self.DataHandlerObj.getStatusInfoString(status))
            self.FileObj.WritetoCVS(datas, labels);
            print('end the loop \n')


server_PC = Server_PC();
server_PC.run();




                    
                

