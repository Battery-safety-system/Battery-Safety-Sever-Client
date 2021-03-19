import minimalmodbus
import time
import json
import sys
sys.path.append("/home/pi/Desktop/Battery-Safety-Sever-Client")
from main.Tools.ClientDataHandler import DataHandler

class ModbusHandler:
    def __init__(self):
        self.openModbus();
        # wait until tht battery voltage meet the requirement
        self.DataHandlerObj = DataHandler();
        self.DataHandlerObj.LoopIfNotMeetReq(self.checkIfModbusInit, 3)

        # start work; set init variable and current;
        self.CurrentList = [0, 1, 0, -1];
        self.currentVal = 3;
        self.PowerList = [];
        self.PreviousTime = time.time();
        self.intervalCount = 0;
        # set the ini
        self.setCurrent(self.currentVal * self.CurrentList[self.intervalCount % 4]);
        self.DataHandlerObj.LoopIfNotMeetReq(self.checkIfModbusCurrentRight, 0, -0.1, 0.1)

    def setAsZero(self):
        self.setCurrent(0);
        self.setMaxDischarge(0)
        self.setMaxCharge(0)
        self.setDCMaxVoltage(0)
        self.setDCMinVoltage(0);
        pass;


    def updateCurrent(self):
        currentTime = time.time();
        if (currentTime - self.PreviousTime > 300):
            self.intervalCount += 1;
            self.PreviousTime = time.time();
            currentVal = self.currentVal * self.CurrentList[self.intervalCount % 4]
            self.setCurrent(currentVal);
            self.DataHandlerObj.LoopIfNotMeetReq(self.checkIfModbusCurrentRight, currentVal, currentVal - 0.1, currentVal + 0.1)


    def openModbus(self):
        with open('config.properties') as f:
            data = json.load(f)
        # open the minimalmodbus device
        USB_Port = data["USB_Port"];
        self.instrument = minimalmodbus.Instrument(USB_Port, 2)  # port name, slave address (in decimal)
        # init the security code heart beat
        # Go to security code register #41025 and enter the number 125.
        self.instrument.write_register(41024, 125, 1)  #
        #  heart beat counter is located at address #41027.
        self.instrument.write_register(41025, 333, 1)  #
        # set current as 0;
        self.setCurrent(0);
        self.setMaxDischarge(110)
        self.setMaxCharge(110)
        self.setDCMaxVoltage(384)
        self.setDCMinVoltage(264);


    def setCurrent(self, value):
        self.instrument.write_register(41026, 1, 1)  # K_op_mode
        self.instrument.write_register(41027, value, 1)  # Op_mode_setpoint

    def setPower(self, value):
        self.instrument.write_register(41026, 2, 1) # K_op_mode
        self.instrument.write_register(41027, value, 1) # Op_mode_setpoint

    def getCurrent(self):
        DCBusCurrent = self.instrument.read_register(30267);
        return DCBusCurrent;

    def getPower(self):
        DCBusPower = self.instrument.read_register(30266);
        return DCBusPower;

    def getVoltage(self):
        DCBusVoltage = self.instrument.read_register(30265);
        return DCBusVoltage

    def checkIfModbusInit(self):
        DCBusPower = self.getPower();
        DCBusCurrent = self.getCurrent();
        DCBusVoltage = self.getVoltage();
        if (DCBusPower == 0 and DCBusCurrent == 0 and DCBusVoltage < 384 and DCBusVoltage > 264):
            return True;
        else:
            return False;

    def checkIfModbusCurrentRight(self, upLine, bottomLine):
        current = self.getCurrent();
        if (current < upLine and current > bottomLine):
            return True;
        else:
            return False;

    def checkIfModbusVoltageRight(self,  upLine, bottomLine):
        voltage = self.getVoltage();
        if (voltage < upLine and voltage > bottomLine):
            return True;
        else:
            return False;

    def checkIfModbusPowerRight(self,  upLine, bottomLine):
        power = self.getPower();
        if (power < upLine and power > bottomLine):
            return True;
        else:
            return False;

    def setDCMinVoltage(self, val):
        self.instrument.write_register(41029, val, 1) # Op_mode_setpoint
        pass;
    def setDCMaxVoltage(self, val):
        self.instrument.write_register(41028, val, 1)  # Op_mode_setpoint
        pass;
    def setMaxCharge(self, val):
        self.instrument.write_register(41030, val, 1)  # Op_mode_setpoint
        pass;
    def setMaxDischarge(self, val):
        self.instrument.write_register(41031, val, 1)  # Op_mode_setpoint
        pass;

