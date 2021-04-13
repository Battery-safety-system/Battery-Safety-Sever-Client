#!/usr/bin/python3
import sys
sys.path.append("/home/pi/Desktop/Battery-Safety-Sever-Client")
from main.Tools.ClientConnection import PCConnection
from main.Tools.File import File
from main.Tools.PcanConnection import PcanConnection
from main.Tools.Status import Status
from main.Tools.ArduinoHandler import ArduinoHandler;
from main.Tools.ModbusHandler import ModbusHandler;

import time;


class Battery_System:
    def __init__(self):

        print("Initialize PCAN")
        PcanLabels = [];
        try:
            PcanLabels = self.pcanInit();
        except Exception as e:
            print(e)
            return ;
            # print("")
        print("********************************************")

        print("Initialize status")
        status_labels = self.statusInit();
        print("********************************************")

        print("Init Arduino")
        try:
            ArduinoLabelList = self.arduinoInit();
        except Exception as e:
            print(e);
            return ;
        print("********************************************")

        #         # init the PC Connection
        #         print("initialize PC Connection")

        print("Init Modbus")
        modbusLabels = []
        try:
            modbusLabels = self.modbusInit();
        except Exception as e:
            print(e);
            self.closeAllDevice();
            return ;
        print("********************************************")


        print("Init Label lists and datas")
        self.createLabelsAndInitDatas(PcanLabels, ArduinoLabelList, modbusLabels, status_labels);
        print("initialize Floder and Files")
        self.FileObj = File(self.label_list)
        print("********************************************")


        print("Init State Machine")
        self.stateInit();
        print("********************************************")


    def pcanInit(self):
        self.PcanConnectionObj = PcanConnection();
        PcanLabels = self.PcanConnectionObj.getLabels();
        print("pcan labels " + str(PcanLabels))
        return PcanLabels;

    def statusInit(self):
        print("initialize Status")
        self.StatusObj = Status()
        status_labels = self.StatusObj.getLabels();
        # print("status labels " + str(status_labels))
        return status_labels;


    def arduinoInit(self):

        self.ArduinoHandlerObj = ArduinoHandler();
        self.ArduinoHandlerObj.ReceiveInfoFromArduino()  # get temp1, temp2, real1, real2 values
        ArduinoLabelList = self.ArduinoHandlerObj.getLabListFromContentDict()
        self.ArduinoHandlerObj.initPumpFanRelay();

        return ArduinoLabelList;


    def modbusInit(self):
        self.ArduinoHandlerObj.initRelayStepOne()
        currentControlMode = 1;
        powerControlMode = 2;
        self.ModbusHandlerObj = ModbusHandler(powerControlMode);
        modbusLabels = self.ModbusHandlerObj.getLabels();
        self.ArduinoHandlerObj.initRelayStepTwo()
        return modbusLabels;


    def createLabelsAndInitDatas(self, PcanLabels, ArduinoLabelList, modbusLabels, status_labels):
        self.label_list = PcanLabels + ArduinoLabelList + modbusLabels + status_labels;
        self.label_list.insert(0, 'time');
        self.label_list.insert(0, 'date');  # final_label_list: [date time BMU01_Max_temp .... BMU02_Max_temp ...]
        self.label_list.append("CurrentState")
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
            print(self.ModbusHandlerObj.info_dict)
            # print(vars(self.StatusObj))

            if self.currentState == self.normalState:
                print("normal state \n")
                self.normalHandler();
            elif self.currentState == self.warningState:
                print("warning state \n")
                self.warningHandler();
            elif self.currentState == self.dangerousState:
                print("dangerous state \n")
                self.dangerousHandler();
            elif self.currentState == self.securityState:
                print("security state \n")
                self.securityHandler();
                break;
            else:
                break;

            print("---------------------------------------")
        print("already in safe mode, the program exit")

    def normalHandler(self):

        self.collectData();

        self.storeDate();

#         self.transferToPc();

        self.ModbusHandlerObj.run();

        self.updateStatusInNormalWarningState();

    def warningHandler(self):

        self.collectData();

        self.storeDate();

        self.activeDeviceInWarningState();

#         self.transferToPc();

        self.updateStatusInNormalWarningState();
        #

    def dangerousHandler(self):

        self.collectData();

        self.storeDate();

        self.ModbusHandlerObj.closeModbus();
        
        self.ArduinoHandlerObj.setRelayoff();

#         self.transferToPc();

        self.updateStatusInDangerousState();

    def securityHandler(self):
        
        self.ModbusHandlerObj.closeModbus();
        print("Modbus off")
        self.ArduinoHandlerObj.setRelayoff();
        self.ArduinoHandlerObj.setPumpFanOff();
        self.ArduinoHandlerObj.closeArduionConnection();
        print("Arduino off")
        self.PcanConnectionObj.close();
        print("pcan off")
        pass;

# -------------------------------------------- State Function ------------------------------------------


    def collectData(self):
        # print("collect Data in client-version5.py")
        # print("Initiate the status ")
        self.StatusObj.InitStatus();

        # print("start the Pcan Module")
        try:
            self.PcanConnectionObj.getAllInfo();
        except Exception as e:
            print(e)
            raise Exception("Error!!!! PcanConnection cannot getAllInfo")
        pcanDatas = self.PcanConnectionObj.getDatas();
        pcanLabels = self.PcanConnectionObj.getLabels();
        self.PcanConnectionObj.detectStatus(self.StatusObj);

        # get label, datas from arduino( mainly temp, pressure)
        # print("Recieve information from Arduino")
        try:
            self.ArduinoHandlerObj.ReceiveInfoFromArduino()  # get temp1, temp2, real1, real2 values
        except:
            print("Error on Arduino Reading, Please check Arduino Connection")
        ArduinoLabelList = self.ArduinoHandlerObj.getLabListFromContentDict()
        ArduinoDataList = self.ArduinoHandlerObj.getDataListFromContentDict();


        # get labels, data from modbus (mainly DC current, DC power)
        try:
            self.ModbusHandlerObj.run();
        except Exception as e:
            print("Error on Modbus Reading, Please check Modbus connection")
        modbus_labels = self.ModbusHandlerObj.getLabels();
        modbus_datas = self.ModbusHandlerObj.getDatas();
        self.ModbusHandlerObj.setStatusByVoltageInNormalWarningState(self.StatusObj)

        # get all the labels and datas from status
        status_labels = self.StatusObj.getLabels();
        status_datas = self.StatusObj.getStatusDatas();

        # merge status, arduino, modbus, pcan to data list and label list, and status dict;
        self.createLabelsAndInitDatas(pcanLabels + ArduinoLabelList + modbus_labels + status_labels);
        self.data_list = pcanDatas + ArduinoDataList + modbus_datas + status_datas;
        self.data_list.insert(0, time.strftime('%H:%M:%S'))
        self.data_list.insert(0, time.strftime('%d-%m-%Y'))
        self.data_list.append(self.convertStateToStr(self.currentState));


    def storeDate(self):
        print("Store Labels, Status, datas to Repository")
        self.FileObj.WritetoCVS(self.data_list, self.label_list);

    def transferToPc(self):
        # send data, label to the pcupdateStatus
        print("send Label, status, datas to PC")
        if len(self.label_list) != len(self.data_list):
            return ;
        dictContent = {self.label_list[i]: self.data_list[i] for i in range(len(self.label_list))}
        try:
            self.PCConnectionObj.sendContent(dictContent)
        except Exception as e:
            self.PCConnectionObj.reconnectAfterLoops();



    def updateStatusInDangerousState(self):
        if(self.ModbusHandlerObj.checkIfModbusVoltageInit() and not self.StatusObj.istempHighVio()):
            self.currentState = self.securityState;



    def updateStatusInNormalWarningState(self):

        if self.StatusObj.dangerous:
            self.currentState = self.dangerousState;
        elif self.StatusObj.warning:
            self.currentState = self.warningState;
        else:
            self.currentState = self.normalState;

    def activeDeviceInWarningState(self):
        # active the device and check if its out of warnig level and dangerous level and do responding operation from status
        # print("activate device: pump and relay with Arduino")
        if (self.StatusObj.istempHighVio()):
            self.ArduinoHandlerObj.setPumpFanOn();

        if self.StatusObj.isVoltageVio():
            if self.StatusObj.isVoltageLowVio():
                self.ModbusHandlerObj.setModbusCharge();
            else:
                self.ModbusHandlerObj.setModbusDischarge();

    def closeAllDevice(self):
        try:
            self.ModbusHandlerObj.closeModbus();
        except Exception as e:
            print(e)
        print("Modbus off")
        self.ArduinoHandlerObj.setRelayoff();
        self.ArduinoHandlerObj.setPumpFanOff();
        self.ArduinoHandlerObj.closeArduionConnection();
        print("Arduino off")
        self.PcanConnectionObj.close();
        print("pcan off")

# ------------------------------------------ monitor Function ---------------------------------------------
    def monitorWarningDangerousStatus(self, statusObj):
        assert isinstance(statusObj, Status)
        dict_status = vars(statusObj)
        warningAndDangerousList = [];
        for ele in dict_status:
            content = dict_status[ele]
            if(content == True):
                warningAndDangerousList.append(ele);
        print("warning and dangerous list: " + str(warningAndDangerousList))


# ------------------------------------ Tools Function ---------------------------------------
    def convertStateToStr(self):
        if(self.currentState == 1):
            return "normalState"
        elif (self.currentState == 2):
            return "warningState"
        elif(self.currentState == 3):
            return "dangerousState"
        elif (self.currentState == 4):
            return "securityState"

    # def __del__(self):
    #     self.closeAllDevice();

try:
    Battery1 = Battery_System();
    Battery1.run();
except:
    print("Battery Error!!! Close all the system")
    Battery1.closeAllDevice();
# try:
#
# except:
#     Battery1.closeAllDevice();










