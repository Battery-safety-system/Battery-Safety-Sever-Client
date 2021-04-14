import serial
import csv
import json
import sys
sys.path.append("/home/pi/Desktop/Battery-Safety-Sever-Client")
from main.Tools.Status import Status
import time;
import logging
logging.basicConfig(filename='../Client/Modbus Status.log', level=logging.DEBUG)
class ArduinoHandler:
    def __init__(self):
        self.ser = serial.Serial('/dev/ttyACM0', 9600, timeout=10)
        # output device
        self.setPINValue();
        self.ohmsList = [];
        self.tempList = [];
        self.setOhmsTempList();
        self.labels = ["Ardu_Temp1", "Ardu_Temp2",  "Ardu_Press"];
        # input device
        self.contentDict = {};  # "Ardu_Temp1": 36, "Ardu_Temp2": 37, "Ardu_Press": 100

        print("Arduino Init complete")


    def initRelayStepOne(self):
        ArduinoInfoList = []
        ArduinoInfoList.append({"device": "Relay", "pin_number": self.Relay1PIN, "pin_value": 1});
        ArduinoInfoList.append({"device": "Relay", "pin_number": self.Relay2PIN, "pin_value": 1});
        self.activateDevice(ArduinoInfoList)
        print("initRelayStepOne: time sleep 15s")
        time.sleep(10)
        pass
    def initRelayStepTwo(self):
        ArduinoInfoList = []
        ArduinoInfoList.append({"device": "Relay", "pin_number": self.Relay2PIN, "pin_value": 1});
        self.activateDevice(ArduinoInfoList)
        print("initRelayStepTwo: time sleep 15s")
        time.sleep(10)
        ArduinoInfoList = []
        ArduinoInfoList.append({"device": "Relay", "pin_number": self.Relay3PIN, "pin_value": 0});
        self.activateDevice(ArduinoInfoList)
        pass
        
    def setPINValue(self):
        with open('../Client/config.properties') as f:
            data = json.load(f)
        data = data["ArduinoHandler"]
        self.pumpPIN = data["pumpPIN"];
        self.FanPIN = data["FanPIN"];
        self.Relay1PIN = data["Relay1PIN"];
        self.Relay2PIN = data["Relay2PIN"];
        self.Relay3PIN = data["Relay3PIN"];


    def setOhmsTempList(self):
        ohmsList = [];
        tempList = [];
        with open('TempSensor.csv', newline='') as csvfile:
            spamreader = csv.reader(csvfile, delimiter=',')
            for row in spamreader:
                ohms = float(row[1]);
                temp = float(row[0])
                ohmsList.append(ohms)
                tempList.append(temp)
        self.tempList = tempList
        self.ohmsList = ohmsList;

    def initPumpFanRelay(self):
        self.setRelayoff();
        self.setPumpFanOff();
# ---------------------------Tools Section -------------------------------
    def receive(self):
        return self.ser.readline().decode("utf-8");

    def send(self, contentStr):
        self.ser.write(contentStr);

# ---------------------------Main Function -----------------------------
    def getLabListFromContentDict(self):
        return self.labels

    def getDataListFromContentDict(self):
        dataList = [];
        labelList = self.getLabListFromContentDict();
        for ele in labelList:
            dataList.append(self.contentDict[ele])
        return dataList

    def closeArduionConnection(self):
        self.ser.close();
        pass;
# ---------------------------Receive Section ----------------------------
    def LoopObserveFunctionRead(self, callBackFun, checkFun, times, *args, **kwargs):
        for i in range(times):
            try:
                content = callBackFun(*args);
                if(checkFun(content)):
                    return content ;
            except Exception as e:
                continue;
        return None;

    def LoopObserveFunctionWrite(self, callBackFun, times, *args, **kwargs):
        for i in range(times):
            try:
                callBackFun(*args)
                return True;
            except Exception as e:
                continue;
        return False;


    def ReceiveInfoFromArduino(self):
        currentTime = time.time();
        contentStr = self.LoopObserveFunctionRead(self.receive, self.checkIfInfoRightFromArduino, 3);
        print("Arduino REading: " + str(contentStr))
        if (contentStr == None ):
            logging.error("ArduinoHandler: ReceiveInforFromArduino: Receive Error!!")
            raise Exception("ArduinoHandler: ReceiveInfoFromArduino: contentStr is not right...")

        contentArr = contentStr.split(',');
        contentDict = {};
        for oneInfo in contentArr:
            arr = oneInfo.split(':');
            keyword = arr[0];
            content = arr[1];
            val = int(content);

            if (keyword[5:9] == "Temp"):
                res = self.convertTempToRealValue(val);
                contentDict[keyword] = int(res);
            elif (keyword[5:9] == "Pres"):
                res = self.convertPressToRealValue(val);
                contentDict[keyword] = int(res);
        self.contentDict = contentDict;

    def checkIfInfoRightFromArduino(self, contentStr):
        assert isinstance(contentStr, str)
        try:
            contentArr = contentStr.split(',')
            for oneInfo in contentArr:
                arr = oneInfo.split(':');
                keyword = arr[0];
                content = arr[1];
                val = int(content);
                if (not (keyword[5:9] == "Temp" or keyword[5:9] == "Pres")):
                    return False
            return True;
        except:
            return False;

    def convertTempToRealValue(self, Volval):
        voltage = (Volval /1024.0 * 5.0)
        # print(voltage)
        ohms = (2200 * voltage) / (5.0 - voltage)
        for i in range(1, len(self.ohmsList)):
            val = self.ohmsList[i];
            if (val >= ohms ) :
                topline = val;
                bottomline = self.ohmsList[i - 1]
                if(bottomline > ohms):
                    return 140;
                per = (ohms - bottomline)/(topline - bottomline)
                temp_high = self.tempList[i - 1];
                temp_low = self.tempList[i];
                temp = (temp_high - temp_low) * per + temp_low;
                return temp
                pass
        return -1;

    def convertPressToRealValue(self, Volval):
        press_high_bar = 150;
        press_low_bar = 0;
        volVal_high_bar = 4.5
        volVal_low_bar = 0.5
        voltage = (Volval /1024.0 * 5.0);
        press = -1;
        if(voltage < volVal_low_bar) :
            press = press_low_bar;
        elif (voltage > volVal_high_bar):
            press = press_high_bar;
        else:
            press = (voltage - volVal_low_bar) /(volVal_high_bar - volVal_low_bar) * press_high_bar
        return  press;

# ----------------------------- Sending Section --------------------------------

    def activateDevice(self, ArduinoInfoList):
        contentStr = "";
        if (ArduinoInfoList == []):
            return;
        for arduinoInfo in ArduinoInfoList:
            contentStr += str(arduinoInfo['pin_number'] ) + ":" + str(arduinoInfo['pin_value']) + "&";
        contentStr = contentStr[0:len(contentStr) - 1];
        if(not self.LoopObserveFunctionWrite(self.send, 3, contentStr.encode())):
            raise Exception("ArduinoHandler: activateDevice: Error!!! cannot send ArduinoInfoList, devices cannot open correctly!!!");



# ------------------------------ setting Section --------------------------------------------------
    def judgePumpFanInfo(self, StatusObj):
        assert isinstance(StatusObj, Status)
        ## logic: get info list
        ArduinoInfoList = [];
        if (StatusObj.isPcanTempWarning  or StatusObj.isPcanTempDangerous):
            logging.error("StatusObj isPcanTempWarning" + str(StatusObj.isPcanTempWarning));
            logging.error("StatusObj isPcanTempDangerous" + str(StatusObj.isPcanTempDangerous));
            ArduinoInfoList.append({"device": "Pump", "pin_number": self.pumpPIN, "pin_value": 1});
            ArduinoInfoList.append({"device": "Fan", "pin_number": self.FanPIN, "pin_value": 1});
            print("temperature is too high, the pump continue to work");
        else:
            print("temp is in control, the pump is off")
            ArduinoInfoList.append({"device": "Pump", "pin_number": self.pumpPIN, "pin_value": 0});
            ArduinoInfoList.append({"device": "Fan", "pin_number": self.FanPIN, "pin_value": 0});
        return ArduinoInfoList;

    def setPumpFanOn(self):
        ArduinoInfoList = [];
        ArduinoInfoList.append({"device": "Pump", "pin_number": self.pumpPIN, "pin_value": 1});
        ArduinoInfoList.append({"device": "Fan", "pin_number": self.FanPIN, "pin_value": 1});
        try:
            self.activateDevice(ArduinoInfoList);
        except Exception as e:
            raise("ArduinoHandler_setPumpFanOn: " + e)
    def setPumpFanOff(self):
        ArduinoInfoList = [];
        ArduinoInfoList.append({"device": "Pump", "pin_number": self.pumpPIN, "pin_value": 0});
        ArduinoInfoList.append({"device": "Fan", "pin_number": self.FanPIN, "pin_value": 0});
        try:
            self.activateDevice(ArduinoInfoList);
        except Exception as e:
            raise ("ArduinoHandler_setPumpFanOff: " + e)

    def setRelayoff(self):
        ArduinoInfoList = []
        ArduinoInfoList.append({"device": "Relay", "pin_number": self.Relay1PIN, "pin_value": 0});
        ArduinoInfoList.append({"device": "Relay", "pin_number": self.Relay2PIN, "pin_value": 0});
        ArduinoInfoList.append({"device": "Relay", "pin_number": self.Relay3PIN, "pin_value": 0});
        try:
            self.activateDevice(ArduinoInfoList);
        except Exception as e:
            raise Exception("ArduinoHandler_setRelayoff: " + str(e))


