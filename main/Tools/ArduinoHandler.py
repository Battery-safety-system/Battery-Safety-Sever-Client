import serial
class ArduinoHandler:
    def __init__(self):
        self.ser = serial.Serial('/dev/ttyACM1', 9600)
        self.pumpPIN = 4;
        self.relayPIN = 5;
        print("check if serial works")
        assert self.ser.readline() == "Arduino Start"
        pass

    def receive(self):
        return self.ser.readline();

    def send(self, contentStr):
        self.ser.write(contentStr);


    def getInfo(self, contentStr):
        print("get All Information from Arduino")
        contentArr = contentStr.split(',');
        contentDict = {};
        for oneInfo in contentArr:
            arr = oneInfo.split(',');
            keyword = arr[0];
            content = arr[1];
            contentDict[keyword] = int(content);
        print("contentDict is: " + str(contentDict))
        return contentDict;

    def activateDevice(self, ArduinoInfoList):
        contentStr = "";
        for arduinoInfo in ArduinoInfoList:
            contentStr += str(arduinoInfo['pin_number'] ) + ":" + str(arduinoInfo['pin_value']) + "&";
        contentStr = contentStr[0:len(contentStr) - 1];
        self.send(contentStr);

    def judgeArduinoInfo(self, StatusObj):
        ArduinoInfoList = [];
        if (StatusObj.istempHigh == True):
            ArduinoInfoList.append({"device": "Pump", "pin_number": self.pumpPIN, "pin_value": 1});
            print("temperature is too high, the pump continue to work");
        else:
            print("temp is in control, the pump is off")
            ArduinoInfoList.append({"device": "Pump", "pin_number": self.pumpPIN, "pin_value": 0});

        if (StatusObj.isvolLimited == True or StatusObj.isCVViolated):
            ArduinoInfoList.append({"device": "Relay", "pin_number": self.relayPIN, "pin_value": 0});
            print("voltage is out of control, relay is off")

        else:
            ArduinoInfoList.append({"device": "Relay", "pin_number": self.relayPIN, "pin_value": 1});
            print("voltage is in control, the relay is on")
        return ArduinoInfoList;

