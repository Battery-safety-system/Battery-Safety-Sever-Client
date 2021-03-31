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
        PcanLabels = self.PcanConnectionObj.getLabels();

        # init Status
        print("initialize Status")
        self.StatusObj = Status()
        status_labels = self.StatusObj.getLabels();
        # init DataHandler
        print("initialize Data Handler")
        self.DataHandlerObj = DataHandler();  # detect the temp and get data  dict list
        # initiate GPIO Handler
        print("initialize GPIO Handler")
        self.GPIOHandlerObj = GPIOHandler();



        # Init Arudino
        print("Init Arduino")
        self.ArduinoHandlerObj = ArduinoHandler();
        ArduinoInfoDict = self.ArduinoHandlerObj.getInfo()  # get temp1, temp2, real1, real2 values
        ArduinoLabelList = self.ArduinoHandlerObj.getLabListFromContentDict(ArduinoInfoDict)

        # Init modbus
        print("Init Modbus")
        self.ModbusHandlerObj = ModbusHandler();
        modbusLabels = self.ModbusHandlerObj.getLabels();

        # start to work;
        self.label_list = PcanLabels + modbusLabels + ArduinoLabelList + status_labels;
        self.data_list = [];

        # init Floder and Files
        print("initialize Floder and Files")
        self.FileObj = File(self.label_list)

        # init the PC Connection
        print("initialize PC Connection")
        self.PCConnectionObj = PCConnection()
        self.PCConnectionObj.connect()
        # self.PCConnectionObj.sendContent({"labels": self.MessageObj.final_label_list})


    def run(self):
        while True:
            print("Begin Loop Module")
            print("current time is " +  time.strftime('%H-%M-%S'))

            print("Initiate the status ")
            self.StatusObj.warning = False;

            print("start the Pcan Module")
            self.PcanConnectionObj.getAllInfo();
            pcanDatas = self.PcanConnectionObj.getDatas();
            pcanLabels = self.PcanConnectionObj.getLabels();
            self.PcanConnectionObj.detectStatus(self.StatusObj);


            # get label, datas from arduino( mainly temp, pressure)
            print("Recieve information from Arduino")
            ArduinoInfoDict = self.ArduinoHandlerObj.getInfo() # get temp1, temp2, real1, real2 values
            ArduinoLabelList = self.ArduinoHandlerObj.getLabListFromContentDict(ArduinoInfoDict)
            ArduinoDataList = self.ArduinoHandlerObj.getDataListFromContentDict(ArduinoLabelList, ArduinoLabelList);
            self.ArduinoHandlerObj.setStatus(self.StatusObj)


            # get labels, data from modbus (mainly DC current, DC power)
            self.ModbusHandlerObj.run();
            modbus_labels = self.ModbusHandlerObj.getLabels();
            modbus_datas = self.ModbusHandlerObj.getDatas();
            self.ModbusHandlerObj.setStatus(self.StatusObj)

            # get all the labels and datas from status
            status_labels = self.StatusObj.getLabels();
            status_datas = self.StatusObj.getStatusList();

            # merge status, arduino, modbus, pcan to data list and label list, and status dict;
            self.label_list = pcanLabels + ArduinoLabelList + modbus_labels + status_labels;
            self.label_list.insert(0, 'time');
            self.label_list.insert(0, 'date');  # final_label_list: [date time BMU01_Max_temp .... BMU02_Max_temp ...]
            self.data_list = pcanDatas + ArduinoDataList + modbus_datas + status_datas;
            self.data_list.insert(0, time.strftime('%H:%M:%S'))
            self.data_list.insert(0, time.strftime('%d-%m-%Y'))

            # store data, label to the local fldoer
            print("Store Labels, Status, datas to Repository")
            self.FileObj.WritetoCVS(self.data_list, self.label_list);

            # active the device and check if its out of warnig level and dangerous level and do responding operation from status

            print("activate device: pump and relay with Arduino")
            ArduinoInfoList = self.ArduinoHandlerObj.judgeArduinoInfo(self.StatusObj);
            self.ArduinoHandlerObj.activateDevice(ArduinoInfoList)


            # # send data, label to the pc
            # print("send Label, status, datas to PC")
            # try:
            #     dictContent = self.DataHandlerObj.getSendContent(data_list, self.StatusObj.getStatusList(), label_list);
            #     self.PCConnectionObj.sendContent(dictContent)
            # except Exception as e:
            #     self.PCConnectionObj.reconnectAfterLoops();


            # GPIOInfoList = self.DataHandlerObj.judgeGPIOInfo(self.StatusObj)  # create GPIO list
            # self.GPIOHandlerObj.activateDevice(GPIOInfoList);



            print("---------------------------------------")
    def __del__(self):
        print("Battery Manage System Program Exit !!!")
        self.ModbusHandlerObj.setAsZero();
        self.PCConnectionObj.close()

        self.GPIOHandlerObj = GPIOHandler(self.DataHandlerObj.getGPIOInitInfoList());

    def warningHandler(self, ModbusHandlerObj):
        assert isinstance(ModbusHandlerObj, ModbusHandler)

    def dangerousHandler(self, ModbusHandlerObj, ArduinoHandlerObj):
        assert isinstance(ModbusHandlerObj, ModbusHandler)
        assert isinstance(ArduinoHandlerObj, ArduinoHandler)


Battery1 = Battery_System();
Battery1.run();











