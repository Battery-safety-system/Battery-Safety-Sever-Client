import serial
import csv
import json
import time;
class ArduinoHandler:
    def __init__(self):
        self.ser = serial.Serial('/dev/ttyACM0', 9600)
        self.setPINValue();
        # output device
        self.labels = ["Ardu_Temp1", "Ardu_Temp2",  "Ardu_Press"];

        print("Arduino Init complete")

    def setPINValue(self):
        with open('../Client/config.properties') as f:
            data = json.load(f)
        data = data["ArduinoHandler"]
        self.pumpPIN = data["pumpPIN"];
        self.FanPIN = data["FanPIN"];
        self.Relay1PIN = data["Relay1PIN"];
        self.Relay2PIN = data["Relay2PIN"];
        self.Relay3PIN = data["Relay3PIN"];

    def setPumpFanOff(self):
        ArduinoInfoList = [];
        ArduinoInfoList.append({"device": "Pump", "pin_number": self.pumpPIN, "pin_value": 0});
        ArduinoInfoList.append({"device": "Fan", "pin_number": self.FanPIN, "pin_value": 0});
        self.activateDevice(ArduinoInfoList);
        
    def setPumpFanOn(self):
        ArduinoInfoList = [];
        ArduinoInfoList.append({"device": "Pump", "pin_number": self.pumpPIN, "pin_value": 1});
        ArduinoInfoList.append({"device": "Fan", "pin_number": self.FanPIN, "pin_value": 1});
        self.activateDevice(ArduinoInfoList);

    def setRelayoff(self):
        ArduinoInfoList = []
        ArduinoInfoList.append({"device": "Relay", "pin_number": self.Relay1PIN, "pin_value": 0});
        ArduinoInfoList.append({"device": "Relay", "pin_number": self.Relay2PIN, "pin_value": 0});
        ArduinoInfoList.append({"device": "Relay", "pin_number": self.Relay3PIN, "pin_value": 0});
        self.activateDevice(ArduinoInfoList);

    def activateDevice(self, ArduinoInfoList):
        contentStr = "";
        for arduinoInfo in ArduinoInfoList:
            contentStr += str(arduinoInfo['pin_number'] ) + ":" + str(arduinoInfo['pin_value']) + "&";
        contentStr = contentStr[0:len(contentStr) - 1];
        self.send(contentStr.encode());
    def receive(self):
        return self.ser.readline().decode("utf-8");

    def send(self, contentStr):
        self.ser.write(contentStr);
        
ar1 = ArduinoHandler();
# ar1.setRelayoff();
# time.sleep(2)
ar1.setPumpFanOff();
print(ar1.receive())
# ar1.setPumpFanOn();
# ArduinoInfoList = []
# ArduinoInfoList.append({"device": "Fan", "pin_number": 7, "pin_value": 0});
# ar1.activateDevice(ArduinoInfoList);