#!/usr/bin/python3


class Status(object):
    """docstring for Status"""
    def __init__(self):
        super(Status, self).__init__()
        print("Initializae Status")
        self.temperature_voliated_battery = [];
        self.battery_cell_voltage_voilated = [];
        
        self.istempHigh = False; 
        self.isvolLimited = False;
        self.isCVViolated = False;

    def getStatusList(self):
        return [self.isvolLimited, self.istempHigh, self.isCVViolated]