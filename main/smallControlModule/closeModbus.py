# !/usr/bin/env python3
import json
import sys
sys.path.append("/home/pi/Desktop/Battery-Safety-Sever-Client")
import minimalmodbus
import time
import logging
from main.Tools.Status import Status

class ModbusHandler:
    def __init__(self, ControlMode):
        logging.basicConfig(filename='Modbus Status.log', level=logging.DEBUG)
        self.ControlMode = ControlMode;

        with open('../Client/config.properties') as f:
            data = json.load(f)
            print(data)
            data = data['ModbusHandler']
            for key in data:
                setattr(self, key, data[key]);
        self.openModbus()

    def openModbus(self):
        # set up connection: port name, slave address (in decimal)
        self.instrument = minimalmodbus.Instrument(self.USB_Port,
                                                   self.slaveAddress)  # port name, slave address (in decimal)
        ### We need to do some special writes before sending commands
        ## Set the security register
        self.instrument.write_register(self.security_code, 125, 0, 6)

        # Set the timeout register
        self.instrument.write_register(self.Heartbeat, 333, 0, 6)
        # set the op mode off
        self.instrument.write_register(self.K_op_mode, 0, 0, 6)  # K_op_mode


    def closeModbus(self):
        self.instrument.write_register(self.K_op_mode, 0, 0, 6)  # K_op_mode


m1 = ModbusHandler(1);
m1.closeModbus(); 