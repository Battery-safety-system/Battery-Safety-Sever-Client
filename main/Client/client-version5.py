#!/usr/bin/python3
import sys
sys.path.append("/home/pi/Desktop/Battery-Safety-Sever-Client/")
from main.Tools.ClientConnection import PCConnection
from main.Tools.File import File
from main.Tools.PcanConnection import PcanConnection
from main.Tools.Status import Status
from main.Tools.ArduinoHandler import ArduinoHandler;
from main.Tools.ModbusHandler import ModbusHandler;

import time;

import logging
class Battery_System:
    def __init__(self):
        logging.basicConfig(filename='Client_Error_Record.log', level=logging.WARNING)
        print("Initialize status")
        status_labels = self.statusInit();
        print("********************************************")

        print("Init Arduino")
        ArduinoLabelList = self.arduinoInit();

        print("********************************************")
        
        
        print("Initialize PCAN")
        PcanLabels = [];
        PcanLabels = self.pcanInit();
        print("********************************************")

        # init the PC Connection
        print("initialize PC Connection")
        self.PcInit();
        print("********************************************")

        print("Init Modbus")
        modbusLabels = []
        modbusLabels = self.modbusInit();
        print("********************************************")



        print("Init Label lists and datas")
        self.createLabelsAndInitDatas(PcanLabels, ArduinoLabelList, modbusLabels, status_labels);
        print("initialize Floder and Files")
        self.FileObj = File(self.label_list)
        print("********************************************")


        print("Init State Machine")
        self.stateInit();
        print("********************************************")

    def __del__(self):
        self.closeAllDevice();

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
        time.sleep(1)
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

            self.monitorWarningDangerousStatus(self.StatusObj)
            self.monitorPcanInfo();
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
        print("already in safe mode, the program exit()")

    def normalHandler(self):
        try:
            self.collectDataInNormalWarningState();
        except Exception as e:
            print(e)
            return;
        self.storeDate();

        self.transferToPc();

        self.ModbusHandlerObj.updateCurrentOrPower();

        self.updateStatusInNormalWarningState();

    def warningHandler(self):
        try:
            self.activeDeviceInWarningState();
            self.collectDataInNormalWarningState();
        except Exception as e:
            print(e);
            self.currentState = self.dangerousState;
            return;

        self.storeDate();

        self.transferToPc();

        self.updateStatusInNormalWarningState();
        #

    def dangerousHandler(self):
        self.activeDeviceInDangerousState();
    
        self.collectDataInDangerousState();

        self.updateStatusInDangerousState();

    def securityHandler(self):
        self.closeAllDevice();
        pass;

# -------------------------------------------- State Function ------------------------------------------

    def collectDataInDangerousState(self):
        try:
            self.PcanConnectionObj.getAllInfo();
            self.PcanConnectionObj.updateStatus(self.StatusObj);
        except Exception as e:
            print(e)


    def collectDataInNormalWarningState(self):
        # print("collect Data in client-version5.py")
        # print("Initiate the status ")
        self.StatusObj.InitStatus();
        try:
            self.PcanConnectionObj.getAllInfo();
            pcanDatas = self.PcanConnectionObj.getDatas();
            pcanLabels = self.PcanConnectionObj.getLabels();
            self.PcanConnectionObj.updateStatus(self.StatusObj);
        except Exception as e:
            # print("client: collectDataInNormalWarningState: Error!!! cannot receive message from pcan")
            logging.error(time.strftime('%H-%M-%S') + "client: collectDataInNormalWarningState: " + "pcanconnection cannot get information");
            raise "client: collectDataInNormalWarningState:" + e;



        # get label, datas from arduino( mainly temp, pressure)
        # print("Recieve information from Arduino")
        try:
            self.ArduinoHandlerObj.ReceiveInfoFromArduino()  # get temp1, temp2, real1, real2 values
            ArduinoLabelList = self.ArduinoHandlerObj.getLabListFromContentDict()
            ArduinoDataList = self.ArduinoHandlerObj.getDataListFromContentDict();
        except Exception as e:
            ArduinoLabelList = [];
            ArduinoDataList = [];
            logging.error(time.strftime('%H-%M-%S') + "client: collectDataInNormalWarningState: " + "arduino cannot get information or the information is not right")
            print(e);



        # get labels, data from modbus (mainly DC current, DC power)
        # improvement: if the modbus handler
        try:
            modbus_labels = self.ModbusHandlerObj.getLabels();
            modbus_datas = self.ModbusHandlerObj.getDatas();
            self.ModbusHandlerObj.setStatusByVoltageInNormalWarningState(self.StatusObj)
        except Exception as e:
            logging.error(time.strftime(
                '%H-%M-%S') + "client: collectDataInNormalWarningState: " + "Modbus cannot get information");
            raise e;



        # get all the labels and datas from status
        status_labels = self.StatusObj.getLabels();
        status_datas = self.StatusObj.getStatusDatas();

        # merge status, arduino, modbus, pcan to data list and label list, and status dict;
        # self.createLabelsAndInitDatas(pcanLabels , ArduinoLabelList , modbus_labels , status_labels);
        self.label_list = pcanLabels + ArduinoLabelList + modbus_labels + status_labels;
        self.label_list.insert(0, 'time');
        self.label_list.insert(0, 'date');  # final_label_list: [date time BMU01_Max_temp .... BMU02_Max_temp ...]
        self.label_list.append("CurrentState")

        self.data_list = pcanDatas + ArduinoDataList + modbus_datas + status_datas;
        self.data_list.insert(0, time.strftime('%H:%M:%S'))
        self.data_list.insert(0, time.strftime('%d-%m-%Y'))
        self.data_list.append(self.convertStateToStr());



    def storeDate(self):
        # print("Store Labels, Status, datas to Repository")
        self.FileObj.WritetoCVS(self.data_list, self.label_list);

    def transferToPc(self):
        try:
            dictContent = {self.label_list[i]: self.data_list[i] for i in range(len(self.label_list))}

#             print("info: client-version5: the content transfer to PC " + str(dictContent))
        except Exception as e:
            print("client-version5: transferToPc: " + e)
            return ;
        try:
            self.PCConnectionObj.sendContent(dictContent)
        except Exception as e:
            print("client-version5: transferToPc: " + str(e));
            return ;



# ------------------ update status in dangerous normal, warning ---------------------------------

    def updateStatusInDangerousState(self):
        try:
            if(not self.ModbusHandlerObj.checkIfModbusVoltageInit()):
                return;
        except:
            pass;
        if( not self.StatusObj.istempHighVio()):
            self.currentState = self.securityState;



    def updateStatusInNormalWarningState(self):

        if self.StatusObj.dangerous:
            self.currentState = self.dangerousState;
        elif self.StatusObj.warning:
            self.currentState = self.warningState;
        else:
            self.currentState = self.normalState;

# ------------------------------- active device in dangerous warning -----------------------------
#     def activeDeviceInNormalState(self):
#         self.ModbusHandlerObj.updateCurrentOrPower();

    def activeDeviceInDangerousState(self):
        if (not self.StatusObj.isModbusOff):
            try:
                self.ModbusHandlerObj.closeModbus();
                self.StatusObj.isModbusOff = True;
            except Exception as e:
                print(e)

        
        if (not self.StatusObj.isRelayOff):
            time.sleep(2)
            try:
                self.ArduinoHandlerObj.setRelayoff();
                self.StatusObj.isRelayOff = True;
            except Exception as e:
                print(e)

        # print("self.StatusObj.isPumpFanOff: " + str(self.StatusObj.isPumpFanOff))
        if (self.StatusObj.istempHighVio() ):
            try:
                self.ArduinoHandlerObj.setPumpFanOn();
                self.StatusObj.isPumpFanOff = False;
            except Exception as e:
                print(e)

    def activeDeviceInWarningState(self):
        # active the device and check if its out of warnig level and dangerous level and do responding operation from status
        # print("activate device: pump and relay with Arduino")
        if (self.StatusObj.istempHighVio()):
            try:
                self.ArduinoHandlerObj.setPumpFanOn();
                self.StatusObj.isPumpFanOff = False;
            except Exception as e:
                raise Exception("client_activeDeviceInWarningState: " + str(e))
            

        if self.StatusObj.isVoltageVio():
            if self.StatusObj.isVoltageLowVio():
                self.ModbusHandlerObj.setModbusCharge();
            else:
                self.ModbusHandlerObj.setModbusDischarge();

    def closeAllDevice(self): # just make sure I do all the operation once,
        try:
            self.ModbusHandlerObj.closeModbus();
            print("Modbus off")
        except Exception as e:
            print(e)

        try:
            self.ArduinoHandlerObj.setRelayoff();
            print("set Relay off")
            self.ArduinoHandlerObj.setPumpFanOff();
            self.StatusObj.isPumpFanOff = True;
            print("Arduino off")
        except Exception as e:
            print(e)
            print("client-version5: closeAllDevice: Arduino off fail")

        try:
            self.PcanConnectionObj.close();
            print("pcan off")
        except Exception as e:
            print(e)
            print("client-version5: closeAllDevice: Pcan off fail")


# ------------------------------------------ monitor Function ---------------------------------------------
    def monitorWarningDangerousStatus(self, statusObj):
        assert isinstance(statusObj, Status)
        print("ModbusHandlerObj.info_dict: " + str(self.ModbusHandlerObj.info_dict))
        dict_status = vars(statusObj)
        warningAndDangerousList = [];

        for ele in dict_status:
            content = dict_status[ele]
            if (ele == "isPumpFanOff" and not dict_status[ele] ):
                print("isPumpFanOff: False, Temperature High!!")
            elif(content == True ):
                warningAndDangerousList.append(ele);
        for ele in warningAndDangerousList:
            print(ele + " : " + str(dict_status[ele]))
        print("warning and dangerous list: " + str(warningAndDangerousList))

    def monitorPcanInfo(self):
#         print("self.label_list: " + str(self.label_list))
#         print("self.data_list: " + str(self.data_list))
        try:
            dictContent = {self.label_list[i]: self.data_list[i] for i in range(len(self.label_list))};
        except Exception as e:
#             print("")
            return; 
        maximum_CMA_Voltage = -1000
        minimum_CMA_Voltage = 1000;
        for ele in dictContent:
            if "CMA_Voltage" in ele:
                val = dictContent[ele]
                if(val > maximum_CMA_Voltage):
                    maximum_CMA_Voltage = val;
                if(val < minimum_CMA_Voltage):
                    minimum_CMA_Voltage = val;
        print("maximum_CMA_Voltage: " + str(maximum_CMA_Voltage));
        print("minimum_CMA_Voltage: " + str(minimum_CMA_Voltage));
# ***************************************************************
        max_temp = -1;
        for ele in dictContent:
            if "CMA_Max_Temp" in ele:
                CMA_Max_Temp = dictContent[ele];
                if max_temp < CMA_Max_Temp:
                    max_temp = CMA_Max_Temp
        print("Max temp: " + str(max_temp))
# ******************************************************************
        Max_Cell_Voltage = -1;
        Min_Cell_Voltage = 1000;
        for ele in dictContent:
            if "Cell" in ele and "Voltage" in ele and "13" not in ele and "14" not in ele:
                cell_voltage = dictContent[ele]
#                 print(ele)
                if (cell_voltage > Max_Cell_Voltage):
                    Max_Cell_Voltage = cell_voltage;
                if (cell_voltage < Min_Cell_Voltage):
                    Min_Cell_Voltage = cell_voltage;
        print("Max_Cell_Voltage: " + str(Max_Cell_Voltage));
        print("Min_Cell_voltage: " + str(Min_Cell_Voltage))


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

    def __del__(self):
        
        self.closeAllDevice();

Battery1 = Battery_System();
Battery1.run();
# try:
#     Battery1 = Battery_System();
#     Battery1.run();
# except Exception as e:
#     print(e)
# 
#     Battery1.closeAllDevice();
# try:
#
# except:
#     Battery1.closeAllDevice();











