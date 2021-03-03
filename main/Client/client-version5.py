#!/usr/bin/python3
import RPi.GPIO as GPIO
from main.Tools.File import File
from main.Tools.PcanConnection import PcanConnection
from main.Tools.Message import Message
from main.Tools.PCConnection import PCConnection
from main.Tools.Status import Status
from main.Tools.GPIOHandler import GPIOHandler
from main.Tools.DataHandler import DataHandler


class Battery_System:
    def __init__(self):
        self.DataHandlerObj = DataHandler();  # detect the temp and get data  dict list
        # initiate GPIO
        self.GPIOHandlerObj = GPIOHandler(GPIO.BCM, self.DataHandlerObj.getGPIOInitInfoList());

        # init the Message
        self.MessageObj = Message();

        # init PcanConnectionOBJ
        self.PcanConnectionObj = PcanConnection();
        self.PcanConnectionObj.getAllInfo(self.MessageObj);  # getLabel, dbcCreating requestMessage SyncMessage
        # init the File
        self.FileObj = File();  # fileinit
        # init the PC Connection
        self.PCConnectionObj = PCConnection();
        self.PCConnectionObj.connect();
        self.PCConnectionObj.sendContent("Label", self.MessageObj.final_label_list);

        self.StatusObj = Status();

    #         self.failConnectTimes = 0;

    def run(self):
        while True:
            self.PcanConnectionObj.getDataFromPcan(self.MessageObj);  # get data dict
            self.DataHandlerObj.handleData(self.MessageObj);  ## build message_data_list
            self.DataHandlerObj.detectStatus(self.StatusObj,
                                             self.MessageObj);  ## set the value for status from messageObj
            self.DataHandlerObj.setStatusToMessageObj(self.StatusObj, self.MessageObj);
            self.DataHandlerObj.storeToLocalRepo(self.FileObj, self.MessageObj);
            try:
                self.PCConnectionObj.sendContent("Data", self.MessageObj.message_data_list);
                self.PCConnectionObj.sendContent("Status", self.DataHandlerObj.getStatusList(self.StatusObj));
            except Exception as e:
                print(e);

            GPIOInfoList = self.DataHandlerObj.judgeGPIOInfo(self.StatusObj)  # create GPIO list
            self.DataHandlerObj.activateDevice(GPIOInfoList);


Battery1 = Battery_System();
Battery1.run();












