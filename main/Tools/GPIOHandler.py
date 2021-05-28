#!/usr/bin/python3
import time
import can
import RPi.GPIO as GPIO
import cantools
import os
import csv
import socket
import pickle

class GPIOHandler(object):
    """docstring for GPIOHandler"""
    def __init__(self):
        self.Pump_PIN = 18;
        self.Relay_PIN = 16;
        self.mode = GPIO.BCM;
        self.Pump_InitValue = GPIO.LOW;
        self.Relay_InitValue = GPIO.HIGH;


    def init(self):
        print("Initialize GPIO Handler")
        GPIO.setwarnings(False)
        GPIO.setmode(self.mode)# BCM
        GPIOInfoList = []
        GPIOInfoList.append({"device": "Pump", "pin_number": self.Pump_PIN, "pin_type": GPIO.OUT, "pin_value": self.Pump_InitValue});
        GPIOInfoList.append({"device": "Relay", "pin_number": self.Relay_PIN, "pin_type": GPIO.OUT, "pin_value": self.Relay_InitValue});
        self.setGPIO(GPIOInfoList);

    def setGPIO(self, GPIOInfoList): # GPIO: device, pin_number, pin_type, pin_value
        for GPIOInfo in GPIOInfoList:
            print("set " + str(GPIOInfo["pin_number"]))
            GPIO.setup(GPIOInfo["pin_number"], GPIOInfo["pin_type"])
            GPIO.output(GPIOInfo["pin_number"], GPIOInfo["pin_value"]);

    def activateDevice(self, GPIOInfoList):
        print("activateDevice() begin")
        for GPIOInfo in GPIOInfoList:
            GPIO.output(GPIOInfo["pin_number"], GPIOInfo["pin_value"]);
        print("activateDevice() end")
