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
    def __init__(self,  GPIOInfoList):
        print("Initialize GPIO Handler")
        super(GPIOHandler, self).__init__()
        GPIO.setwarnings(False)
        GPIO.setmode(GPIO.BCM)# BCM
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
