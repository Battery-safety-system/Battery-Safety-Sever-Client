#!/usr/bin/python3
import time
import can

import cantools
import os

class DataHandler(object):
    """docstring for DataHandler"""
    def __init__(self):
        super(DataHandler, self).__init__()
        print("Initializae Server Data Handler")

    def getLabelFromDict(self, content):
        print("getLabelFromDict() Begin")
        assert isinstance(content, dict)
        assert content["keyword"] == "Label"
        print("getLabelFromDict() End")
        return content["list"];

    def getDataFromDict(self, content):
        print("getDataFromDict() Begin")
        assert isinstance(content, dict)
        assert content["keyword"] == "Data"
        print("getDataFromDict() End")
        return content["list"];

    def getStatusFromDict(self, content):
        print("getStatusFromDict() Begin")
        assert isinstance(content, dict)
        assert content["keyword"] == "Status"
        print("getStatusFromDict() End")
        return content["list"];

    # def printList

    def getDeviceInfoString(self, status):
        str1 = "Device: Pump is "
        if (status[0] == True):
            str1 += "on"
        else:
            str1 += "off"
        str1 += " Relay is "
        if (status[1] == True or status[2] == True):
            str1 += "off"
        else:
            str1 += "on"
        return str1;

    def getStatusInfoString(self, status):
        str1 = "status: isvolLimited: " + str(status[0]) + "istempHigh: " + str(status[1]) + "isCVViolated: " + str(
            status[2])

        return str1;