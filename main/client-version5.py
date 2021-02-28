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
        # initiate GPIO
        self.GPIOHandlerObj = GPIOHandler(GPIO.BCM, self.getGPIOInitInfoList());

        # init the Message
        self.MessageObj = Message();

        # init PcanConnectionOBJ
        self.PcanConnectionObj = PcanConnection();
        PcanConnectionObj.getAllInfo(MessageObj); # getLabel, dbcCreating requestMessage SyncMessage
        # init the File
        self.FileObj = File(); # fileinit
        # init the PC Connection
        self.PCConnectionObj = PCConnection();
        self.PCConnectionObj.connect();
        self.PCConnectionObj.sendContent("Label", self.MessageObj.final_label_list);

        self.DataHandlerObj = DataHandlerObj();
        self.StatusObj = Status();

    def getGPIOInitInfoList(self):
        GPIOInfoList = []
        GPIOInfoList.append({"device": "Pump", "pin_number": 18, "pin_type": GPIO.OUT, "pin_value": GPIO.LOW});
        GPIOInfoList.append({"device": "Relay", "pin_number": 16, "pin_type": GPIO.OUT, "pin_value": GPIO.HIGH});
        return GPIOInfoList

    def getStatusList(self, StatusObj):
        return [StatusObj.isvolLimited, StatusObj.istempHigh, StatusObj.isCVViolated]

    def storeToLocalRepo(self, FileObj, MessageObj):
        FileObj.WritetoCVS(MessageObj.message_data_list, MessageObj.final_label_list);
        pass

    def activateDevice(self, GPIOInfoList):
        print("activateDevice() begin")
        for GPIOInfo in GPIOInfoList:
            GPIO.output(GPIOInfo.pin_number, GPIOInfo.pin_value);
        print("activateDevice() end")

    def judgeGPIOInfo(self, StatusObj):
        GPIOInfoList = [];
        if(StatusObj.tempHigh == True):
            GPIOInfoList.append({"device": "Pump", "pin_number": 18, "pin_type": GPIO.OUT, "pin_value": GPIO.HIGH});
            print("temperature is too high, the pump continue to work");
        else:
            print("temp is in control, the pump is off")
            GPIOInfoList.append({"device": "Pump", "pin_number": 18, "pin_type": GPIO.OUT, "pin_value": GPIO.LOW});

        if(StatusObj.volLimited == True):
            GPIOInfoList.append({"device": "Relay", "pin_number": 16, "pin_type": GPIO.OUT, "pin_value": GPIO.LOW});        
            print("voltage is out of control, break the program")

        else:
            GPIOInfoList.append({"device": "Relay", "pin_number": 16, "pin_type": GPIO.OUT, "pin_value": GPIO.HIGH});        
            print("voltage is in control, the relay is on")
        return GPIOInfoList;

    def run(self):
            while True:
                self.PCConnectionObj.getData();
                self.DataHandler.handleData(self.MessageObj);
                self.DataHandler.detectStatus(self.StatusObj, self.MessageObj);
                self.storeToLocalRepo(self.FileObj, self.MessageObj);
                try:
                    self.PCConnection.sendContent("Data", self.MessageObj.message_data_list);

                    self.PCConnection.sendContent("Status", self.getStatusList(self.StatusObj) );
                except Exception as e:
                    print(e);


                GPIOInfoList = self.judgeGPIOInfo(self.StatusObj)
                self.activateDevice(GPIOInfoList);



Battery1 = Battery_System();
Battery1.run();








