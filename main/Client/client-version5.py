#!/usr/bin/python3

from main.Tools.File import File
from main.Tools.PcanConnection import PcanConnection
from main.Tools.Message import Message
from main.Tools.ClientConnection import PCConnection
from main.Tools.Status import Status
from main.Tools.GPIOHandler import GPIOHandler
from main.Tools.ClientDataHandler import DataHandler

import time;

class Battery_System:
    def __init__(self):
        # init PcanConnectionOBJ
        # check PCAN
        self.PcanConnectionObj = PcanConnection();

        self.MessageObj = Message();
        self.PcanConnectionObj.getAllInfo(self.MessageObj);  # getLabel, dbcCreating requestMessage SyncMessage
        # init Floder and Files
        self.FileObj = File(self.MessageObj.final_label_list)
        # init Status
        self.StatusObj = Status()
        # init DataHandler
        self.DataHandlerObj = DataHandler();  # detect the temp and get data  dict list
        # initiate GPIO Handler
        self.GPIOHandlerObj = GPIOHandler(self.DataHandlerObj.getGPIOInitInfoList());

        # init the PC Connection
        self.PCConnectionObj = PCConnection()
        self.PCConnectionObj.connect()
        self.PCConnectionObj.sendContent({"labels": self.MessageObj.final_label_list})

    def run(self):
        while True:
            # Receive data from Pcan
            print("current time is " +  time.strftime('%H-%M-%S'))

            self.PcanConnectionObj.getDataFromPcan(self.MessageObj);  # get data dict
            # get Status, Labels, datas
            self.DataHandlerObj.handleData(self.MessageObj);  ## build message_data_list
            self.DataHandlerObj.detectStatus(self.StatusObj, self.MessageObj);  ## set the value for status from messageObj
            self.DataHandlerObj.setStatusToMessageObj(self.StatusObj, self.MessageObj);

            # store data to the local repo
            self.FileObj.WritetoCVS(self.MessageObj.message_data_list, self.MessageObj.final_label_list);
            try:
                dictContent = self.DataHandlerObj.getSendContent(self.MessageObj, self.StatusObj);
                self.PCConnectionObj.sendContent(dictContent)
            except Exception as e:
                self.PCConnectionObj.reconnectAfterLoops();

            # active device based on status
            GPIOInfoList = self.DataHandlerObj.judgeGPIOInfo(self.StatusObj)  # create GPIO list
            self.GPIOHandlerObj.activateDevice(GPIOInfoList);
            print("---------------------------------------")
    def __del__(self):
        print("Battery Manage System Program Exit !!!")

        self.PCConnectionObj.close()

        self.GPIOHandlerObj = GPIOHandler(self.DataHandlerObj.getGPIOInitInfoList());


Battery1 = Battery_System();
Battery1.run();












