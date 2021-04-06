#!/usr/bin/python3
import sys

from main.Tools.ClientConnection import PCConnection

sys.path.append("/home/pi/Desktop/Battery-Safety-Sever-Client")
from main.Tools.File import File
from main.Tools.PcanConnection import PcanConnection
from main.Tools.Status import Status
from main.Tools.ArduinoHandler import ArduinoHandler;
from main.Tools.ModbusHandler import ModbusHandler;

import time;


class Battery_System:
    def __init__(self):

        print("Initialize PCAN")
        PcanLabels = self.pcanInit();

        print("Initialize status")
        status_labels = self.statusInit();

        print("Init Arduino")
        ArduinoLabelList = self.arduinoInit();

        print("Init Modbus")
        modbusLabels = self.modbusInit();

        print("Init Label lists and datas")
        self.labelAndDataInit(PcanLabels, ArduinoLabelList, modbusLabels, status_labels);

        print("initialize Floder and Files")
        self.FileObj = File(self.label_list)


#         # init the PC Connection
#         print("initialize PC Connection")

        print("Init State Machine")
        self.stateInit();


    def pcanInit(self):
        # init PcanConnectionOBJ

        self.PcanConnectionObj = PcanConnection();
        PcanLabels = self.PcanConnectionObj.getLabels();
        return PcanLabels;

    def statusInit(self):
        print("initialize Status")
        self.StatusObj = Status()
        status_labels = self.StatusObj.getLabels();
        return status_labels;
        pass;

    def arduinoInit(self):

        self.ArduinoHandlerObj = ArduinoHandler();
        self.ArduinoHandlerObj.ReceiveInfoFromArduino()  # get temp1, temp2, real1, real2 values
        ArduinoLabelList = self.ArduinoHandlerObj.getLabListFromContentDict()
        # Init the device
        ArduinoInfoList = self.ArduinoHandlerObj.judgeArduinoInfo(self.StatusObj);
        self.ArduinoHandlerObj.activateDevice(ArduinoInfoList)

        return ArduinoLabelList;


    def modbusInit(self):
        currentControlMode = 1;
        powerControlMode = 2;
        self.ModbusHandlerObj = ModbusHandler(currentControlMode);
        modbusLabels = self.ModbusHandlerObj.getLabels();
        return modbusLabels;


    def labelAndDataInit(self, PcanLabels, ArduinoLabelList, modbusLabels, status_labels):
        self.label_list = PcanLabels + ArduinoLabelList + modbusLabels + status_labels;
        self.label_list.insert(0, 'time');
        self.label_list.insert(0, 'date');  # final_label_list: [date time BMU01_Max_temp .... BMU02_Max_temp ...]
        self.data_list = [];

    def PcInit(self):
        self.PCConnectionObj = PCConnection()
        self.PCConnectionObj.connect()
        # self.PCConnectionObj.sendContent({"labels": self.MessageObj.final_label_list})


    def stateInit(self):
        self.normalState = 1;
        self.warningState = 2;
        self.dangerousState = 3;
        self.securityState = 4;
        self.currentState = self.normalState;

# ----------------------------------- Running Section --------------------------------------------

    def run(self):
        print("Begin Loop Module")
        while True:
            print("current time is " + time.strftime('%H-%M-%S'))
            if self.currentState == self.normalState:
                self.normalHandler();
            elif self.currentState == self.warningState:
                self.warningHandler();
            elif self.currentState == self.dangerousState:
                self.dangerousHandler();
            elif self.currentState == self.securityState:
                self.securityHandler();
                break;
            else:
                break;

            print("---------------------------------------")
        print("already in safe mode, the program exit")

    def normalHandler(self):

        self.collectData();

        self.storeDate();

        # self.transferToPc();

        self.ModbusHandlerObj.run();

        self.updateStatus();

    def warningHandler(self):

        self.collectData();

        self.storeDate();

        self.activeDevice();

        # self.transferToPc();

        self.updateStatus();
        #

    def dangerousHandler(self):

        self.collectData();

        self.storeDate();

        self.ModbusHandlerObj.closeModbus();
        self.ArduinoHandlerObj.setRelayoff();

        # self.transferToPc();

        self.updateStatus();

    def securityHandler(self):
        self.ModbusHandlerObj.closeModbus();
        self.ArduinoHandlerObj.setRelayoff();
        self.ArduinoHandlerObj.setPumpoff();
        self.ArduinoHandlerObj.closeArduionConnection();
        self.PcanConnectionObj.close();
        pass;

# --------------------------------------------Tools Section ------------------------------------------

    def collectData(self):
        print("collect Data in client-version5.py")
        print("Initiate the status ")
        self.StatusObj.InitStatus();

        print("start the Pcan Module")
        self.PcanConnectionObj.getAllInfo();
        pcanDatas = self.PcanConnectionObj.getDatas();
        pcanLabels = self.PcanConnectionObj.getLabels();
        self.PcanConnectionObj.detectStatus(self.StatusObj);

        # get label, datas from arduino( mainly temp, pressure)
        print("Recieve information from Arduino")
        self.ArduinoHandlerObj.ReceiveInfoFromArduino()  # get temp1, temp2, real1, real2 values
        ArduinoLabelList = self.ArduinoHandlerObj.getLabListFromContentDict()
        ArduinoDataList = self.ArduinoHandlerObj.getDataListFromContentDict();


        # get labels, data from modbus (mainly DC current, DC power)
        self.ModbusHandlerObj.run();
        modbus_labels = self.ModbusHandlerObj.getLabels();
        modbus_datas = self.ModbusHandlerObj.getDatas();
        self.ModbusHandlerObj.setStatus(self.StatusObj)

        # get all the labels and datas from status
        status_labels = self.StatusObj.getLabels();
        status_datas = self.StatusObj.getStatusDatas();

        # merge status, arduino, modbus, pcan to data list and label list, and status dict;
        self.label_list = pcanLabels + ArduinoLabelList + modbus_labels + status_labels;
        self.label_list.insert(0, 'time');
        self.label_list.insert(0, 'date');  # final_label_list: [date time BMU01_Max_temp .... BMU02_Max_temp ...]
        self.data_list = pcanDatas + ArduinoDataList + modbus_datas + status_datas;
        self.data_list.insert(0, time.strftime('%H:%M:%S'))
        self.data_list.insert(0, time.strftime('%d-%m-%Y'))

    def storeDate(self):
        print("Store Labels, Status, datas to Repository")
        self.FileObj.WritetoCVS(self.data_list, self.label_list);

    def transferToPc(self):
        # send data, label to the pc
        print("send Label, status, datas to PC")
        if len(self.label_list) != len(self.data_list):
            return ;
        dictContent = {self.label_list[i]: self.data_list[i] for i in range(len(self.label_list))}
        try:
            self.PCConnectionObj.sendContent(dictContent)
        except Exception as e:
            self.PCConnectionObj.reconnectAfterLoops();



    def updateStatus(self):
        print("Update the value of Modbus based on status")
        if self.currentState == self.dangerousState:
            if not self.StatusObj.dangerous and not self.StatusObj.warning:
                self.currentState = self.securityState;
            return ;

        if self.StatusObj.dangerous:
            self.currentState = self.dangerousState;
        elif self.StatusObj.warning:
            self.currentState = self.warningState;
        else:
            self.currentState = self.normalState;

    def activeDevice(self):
        # active the device and check if its out of warnig level and dangerous level and do responding operation from status
        print("activate device: pump and relay with Arduino")
        ArduinoInfoList = self.ArduinoHandlerObj.judgeArduinoInfo(self.StatusObj);
        self.ArduinoHandlerObj.activateDevice(ArduinoInfoList)
        if self.StatusObj.isVoltageVio():
            if self.StatusObj.isVoltageLowVio():
                self.ModbusHandlerObj.setModbusCharge();
            else:
                self.ModbusHandlerObj.setModbusDischarge();


Battery1 = Battery_System();
Battery1.run();











