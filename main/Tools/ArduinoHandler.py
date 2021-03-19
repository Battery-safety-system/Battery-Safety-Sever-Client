import serial
import csv
class ArduinoHandler:
    def __init__(self):
        self.ser = serial.Serial('/dev/ttyACM0', 9600)
        # output device
        self.pumpPIN = 4;
        self.FanPIN = 8;
        self.Relay1PIN = 5;
        self.Relay2PIN = 6;
        self.Relay3PIN = 7;



        self.ohmsList = [];
        self.tempList = [];
        self.getDictFromSensorCsv();

        # input device
        self.contentDict = {};
        self.inputDeviceList = ["Ardu_Temp1", "Ardu_Temp2", "Ardu_Press" ];
        pass

    def getDictFromSensorCsv(self):
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
            contentDict[keyword] = int(content);
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


    def convertToRealValue(self):
        for ele in self.inputDeviceList:
            val = self.contentDict[ele];

        pass;
    def convertTempToRealValue(self, Volval):
        voltage = (Volval /1024.0 * 5.0)
        ohms = (2200 * voltage) / (5.0 - voltage)
        for i in range(1, len(self.ohmsList)):
            val = self.ohmsList[i];
            if (val >= ohms ) :
                topline = val;
                bottomline =  self.ohmsList[i - 1]
                if(bottomline > ohms):
                    return 140;
                per = (ohms - bottom)(topline - bottomline)
                temp_high = self.tempList[i - 1];
                temp_low = self.tempList[i];
                temp = (temp_high - temp_low) * per + temp_low;
                return 
                pass
        return -1; 

        pass