#!/usr/bin/python3
import time
import can
import RPi.GPIO as GPIO
import cantools
import os
import csv
import socket
import pickle
import logging
from File import File
from PcanConnection import PcanConnection
from Message import Message
from PCConnection import PCConnection
from Status import Status
from GPIOHandler import GPIOHandler
from DataHandler import DataHandler


class Battery_System:
    def __init__(self):
        self.DataHandlerObj = DataHandler(); # detect the temp and get data  dict list
        # initiate GPIO
        self.GPIOHandlerObj = GPIOHandler(GPIO.BCM, self.DataHandlerObj.getGPIOInitInfoList());

        # init the Message
        self.MessageObj = Message();

        # init PcanConnectionOBJ
        self.PcanConnectionObj = PcanConnection();
        self.PcanConnectionObj.getAllInfo(self.MessageObj); # getLabel, dbcCreating requestMessage SyncMessage
        # init the File
        self.FileObj = File(); # fileinit
        # init the PC Connection
        self.PCConnectionObj = PCConnection();
        #self.PCConnectionObj.connect();
        #self.PCConnectionObj.sendContent("Label", self.MessageObj.final_label_list);

        
        self.StatusObj = Status();
#         self.failConnectTimes = 0; 

    def run(self):
            while True:
                self.PcanConnectionObj.getDataFromPcan(self.MessageObj); # get data dict
                self.DataHandlerObj.handleData(self.MessageObj); ## build message_data_list
                self.DataHandlerObj.detectStatus(self.StatusObj, self.MessageObj); ## set the value for status from messageObj
                self.DataHandlerObj.setStatusToMessageObj(self.StatusObj, self.MessageObj);
                self.DataHandlerObj.storeToLocalRepo(self.FileObj, self.MessageObj);
#                 try:
#                     self.PCConnection.sendContent("Data", self.MessageObj.message_data_list);
#                     self.PCConnection.sendContent("Status", self.getStatusList(self.StatusObj) );
#                 except Exception as e:
#                     print(e);


                GPIOInfoList = self.DataHandlerObj.judgeGPIOInfo(self.StatusObj) # create GPIO list
                self.DataHandlerObj.activateDevice(GPIOInfoList);

Battery1 = Battery_System();
Battery1.run();







