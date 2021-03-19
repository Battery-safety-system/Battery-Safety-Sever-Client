#!/usr/bin/python3
import sys
sys.path.append("/home/pi/Desktop/Battery-Safety-Sever-Client")
from main.Tools.File import File
from main.Tools.PcanConnection import PcanConnection
from main.Tools.Message import Message
from main.Tools.ClientConnection import PCConnection
from main.Tools.Status import Status
from main.Tools.GPIOHandler import GPIOHandler
from main.Tools.ClientDataHandler import DataHandler
from main.Tools.ArduinoHandler import ArduinoHandler;
from main.Tools.ModbusHandler import ModbusHandler;
import time;

class Battery_System:
    def __init__(self):
        # init PcanConnectionOBJ
        # check PCAN
        print("check PCAN")
        self.PcanConnectionObj = PcanConnection();
        self.MessageObj = Message();
        self.PcanConnectionObj.getAllInfo(self.MessageObj);  # getLabel, dbcCreating requestMessage SyncMessage
        # init Floder and Files
        print("initialize Floder and Files")
        self.FileObj = File(self.MessageObj.final_label_list)
        # init Status
        print("initialize Status")
        self.StatusObj = Status()
        # init DataHandler
        print("initialize Data Handler")
        self.DataHandlerObj = DataHandler();  # detect the temp and get data  dict list
        # initiate GPIO Handler
        print("initialize GPIO Handler")
        self.GPIOHandlerObj = GPIOHandler(self.DataHandlerObj.getGPIOInitInfoList());

        # init the PC Connection
        print("initialize PC Connection")
        self.PCConnectionObj = PCConnection()
        self.PCConnectionObj.connect()
        self.PCConnectionObj.sendContent({"labels": self.MessageObj.final_label_list})

        # check Arudino
        print("check Arduino")
        self.ArduinoHandlerObj = ArduinoHandler();

        # check modbus
        self.ModbusHandlerObj = ModbusHandler();


    def run(self):
        while True:
            print("Begin Loop Module")
            # Receive data from Pcan
            print("current time is " +  time.strftime('%H-%M-%S'))
            print("Receive Message from PCAN")
            self.PcanConnectionObj.getDataFromPcan(self.MessageObj);  # get data dict

            print("Recieve information from Arduino")
            ArduinoInfoDict = self.ArduinoHandlerObj.getInfo() # get temp1, temp2, real1, real2 values
            ArduinoLabelList = self.ArduinoHandlerObj.getLabListFromContentDict(ArduinoInfoDict)
            ArduinoDataList = self.ArduinoHandlerObj.getDataListFromContentDict(ArduinoLabelList, ArduinoLabelList);

            # get Status, Labels, datas
            print("Get Labels, Status, datas from Message")
            self.DataHandlerObj.handleData(self.MessageObj);  ## build message_data_list
            self.DataHandlerObj.detectStatus(self.StatusObj, self.MessageObj);  ## set the value for status from messageObj
            self.DataHandlerObj.setStatusToMessageObj(self.StatusObj, self.MessageObj);

            # store data to the local repo
            print("Store Labels, Status, datas to Repository")
            data_list = []; label_list = [];
            data_list = self.MessageObj.message_data_list + ArduinoDataList;
            label_list = self.MessageObj.final_label_list + ArduinoLabelList;
            self.FileObj.WritetoCVS(data_list, label_list);

            print("send Label, status, datas to PC")
            try:
                dictContent = self.DataHandlerObj.getSendContent(data_list, self.StatusObj.getStatusList(), label_list);
                self.PCConnectionObj.sendContent(dictContent)
            except Exception as e:
                self.PCConnectionObj.reconnectAfterLoops();

            # active device based on status
            print("activate device: pump and relay")
            ArduinoInfoList = self.ArduinoHandlerObj.judgeArduinoInfo(self.StatusObj);
            self.ArduinoHandlerObj.activateDevice(ArduinoInfoList)
            # GPIOInfoList = self.DataHandlerObj.judgeGPIOInfo(self.StatusObj)  # create GPIO list
            # self.GPIOHandlerObj.activateDevice(GPIOInfoList);

            # update the modbus current
            self.ModbusHandlerObj.updateCurrent();

            print("---------------------------------------")
    def __del__(self):
        print("Battery Manage System Program Exit !!!")
        self.ModbusHandlerObj.setAsZero();
        self.PCConnectionObj.close()

        self.GPIOHandlerObj = GPIOHandler(self.DataHandlerObj.getGPIOInitInfoList());


Battery1 = Battery_System();
Battery1.run();











