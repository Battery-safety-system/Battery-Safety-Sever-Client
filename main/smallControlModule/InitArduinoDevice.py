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