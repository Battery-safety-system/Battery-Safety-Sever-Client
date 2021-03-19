import serial
import csv
import json
class ArduinoHandler:
    def __init__(self):
        self.ser = serial.Serial('/dev/ttyACM0', 9600)
        # output device
        self.setPINValue();



        self.ohmsList = [];
        self.tempList = [];
        self.setOhmsTempList();

        # input device
        self.contentDict = {};  # "Ardu_Temp1": 589, "Ardu_Temp2": 589, "Ardu_Press":620
        # self.inputDeviceList = ["Ardu_Temp1", "Ardu_Temp2", "Ardu_Press" ];
        pass

    def setPINValue(self):
        with open('config.properties') as f:
            data = json.load(f)
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
                ohms = row[1];
                temp = row[0]
                ohmsList.append(ohms)
                tempList.append(temp)
        self.tempList = tempList
        self.ohmsList = ohmsList;

    def receive(self):
        return self.ser.readline().decode("utf-8");

    def send(self, contentStr):
        self.ser.write(contentStr);

    def getLabListFromContentDict(self, contentDict):
        labelList = [];
        for key in contentDict:
            labelList.append(key)
        return labelList;

    def getDataListFromContentDict(self, contentDict, labelList):
        dataList = [];
        for ele in labelList:
            dataList.append(contentDict[ele])
        return dataList

    def getInfo(self):
        contentStr = self.receive();
        print(contentStr, '')
        print("get All Information from Arduino")
        contentArr = contentStr.split(',');
        contentDict = {};
        for oneInfo in contentArr:
            arr = oneInfo.split(':');
            keyword = arr[0];
            content = arr[1];
            val = int(content);

            if(keyword[5:9] == "Temp") :
                res = self.convertTempToRealValue(val);
                contentDict[keyword] = int(res);
            elif(keyword[5:9] == "Pres") :
                res = self.convertPressToRealValue(val);
                contentDict[keyword] = int(res);
            else:
                raise Exception("getInfo: don't have such device");

        print("contentDict is: " + str(contentDict))
        self.contentDict = contentDict;
        return contentDict;

    def activateDevice(self, ArduinoInfoList):
        contentStr = "";
        for arduinoInfo in ArduinoInfoList:
            contentStr += str(arduinoInfo['pin_number'] ) + ":" + str(arduinoInfo['pin_value']) + "&";
        contentStr = contentStr[0:len(contentStr) - 1];
        self.send(contentStr.encode());

    def judgeArduinoInfo(self, StatusObj):
        ## logic: get info list
        ArduinoInfoList = [];
        if (StatusObj.istempHigh == True):
            ArduinoInfoList.append({"device": "Pump", "pin_number": self.pumpPIN, "pin_value": 1});
            ArduinoInfoList.append({"device": "Pump", "pin_number": self.FanPIN, "pin_value": 1});
            print("temperature is too high, the pump continue to work");
        else:
            print("temp is in control, the pump is off")
            ArduinoInfoList.append({"device": "Pump", "pin_number": self.pumpPIN, "pin_value": 0});
            ArduinoInfoList.append({"device": "Pump", "pin_number": self.FanPIN, "pin_value": 0});

        if (StatusObj.isvolLimited == True or StatusObj.isCVViolated):
            ArduinoInfoList.append({"device": "Relay", "pin_number": self.Relay1PIN, "pin_value": 0});
            ArduinoInfoList.append({"device": "Relay", "pin_number": self.Relay2PIN, "pin_value": 0});
            ArduinoInfoList.append({"device": "Relay", "pin_number": self.Relay3PIN, "pin_value": 0});
            print("voltage is out of control, relay is off")

        else:
            ArduinoInfoList.append({"device": "Relay", "pin_number": self.Relay1PIN, "pin_value": 1});
            ArduinoInfoList.append({"device": "Relay", "pin_number": self.Relay2PIN, "pin_value": 1});
            ArduinoInfoList.append({"device": "Relay", "pin_number": self.Relay3PIN, "pin_value": 1});
            print("voltage is in control, the relay is on")
        return ArduinoInfoList;





    def convertTempToRealValue(self, Volval):
        voltage = (Volval /1024.0 * 5.0)
        print(voltage)
        ohms = (2200 * voltage) / (5.0 - voltage)
        for i in range(1, len(self.ohmsList)):
            val = self.ohmsList[i];
            if (val >= ohms ) :
                topline = val;
                bottomline =  self.ohmsList[i - 1]
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
        voltage = (Volval /1024.0 * 5.0);
        press = -1;
        if(voltage < 0.5) :
            press = 0;
        elif (voltage > 4.5):
            press = 150;
        else:
            press = (voltage - 0.5) /(4.5 - 0.5) * 150
        return  press;

        pass