#!/usr/bin/env python3
import minimalmodbus
import time
import logging

class ModbusHandler:
    def __init__(self):
        logging.basicConfig(filename='Modbus Status.log', level=logging.DEBUG)
        self.USB_Port = '/dev/ttyUSB0'
        self.slaveAddress = 2;
        
        self.current_mode = 2;
        self.power_mode = 1;
        self.voltage_mode = 4
        
        self.max_vol = 384
        self.min_vol = 264
        
        self.current_scale = 52.094
        
        self.voltage_scale = 32.767
        self.power_scale = 218.44
        
        # setting register
        self.security_code = 41024
        self.Heartbeat = 41025
        self.K_op_mode = 41026
        self.Op_mode_setpoint = 41027
        self.bat_max_volt = 41028
        self.bat_min_volt = 41029
        self.bat_max_chrg_power = 41032
        self.bat_max_chrg_crt = 41030
        self.bat_max_dischrg_crt = 41031
        # reading register
        self.epcl_dc_link_volt = 30265
        self.epcl_dc_link_pwr = 30266
        self.epc1_dc_link_crnt = 30267

        # the variance
        self.variance_current =  1;
        self.variance_voltage = 20;
        self.variance_power= 5;

        # the initial current, voltage, power values
        self.init_current = 2;
        self.init_power = 5;

        #
        logging.info("Initialize the modbusHandler")
        self.Init();

        # start work; set init variable and current;
        self.CurrentList = [0, 1, 0, -1];
        self.currentVal = 3;

        self.powerValue = 20;
        self.PowerList = [0, 1, 0, -1];

        self.PreviousTime = time.time();
        self.intervalCount = 0;
        self.IntervalTime = 300;

    def updateCurrent(self):
        currentTime = time.time();
        if (currentTime - self.PreviousTime > self.IntervalTime):
            self.intervalCount += 1;
            self.PreviousTime = time.time();
            # get the current value we need
            currentVal = self.currentVal * self.CurrentList[self.intervalCount % 4]
            # set the current value
            self.setCurrent(currentVal);
            # check if the real value is one the range of expected values
            self.LoopIfNotMeetReq(self.checkIfModbusCurrentRight, 20, currentVal - self.variance_current, currentVal + self.variance_current)

    def updatePower(self):
        currentTime = time.time();
        if (currentTime - self.PreviousTime > self.IntervalTime):
            self.intervalCount += 1;
            self.PreviousTime = time.time();
            # get the current value we need
            powerVal = self.powerValue * self.PowerList[self.intervalCount % 4]
            # set the current value
            self.setPower(powerVal);
            # check if the real value is one the range of expected values
            self.LoopIfNotMeetReq(self.checkIfModbusPowerRight, 20, powerVal - self.variance_power, powerVal + self.variance_power)
    def run(self):
        while(True):
            self.updatePower()
            # self.updateCurrent();

    def Init(self):

        logging.info("----------------")
        self.openModbus();

        logging.info("set the limitation on current, voltage, power")
        self.setLimitation();


#         logging.info("set current 0")
#         self.initCurrent();
        
#         logging.info("set power 0")
#         self.initPower();
#         self.setCurrent(-20);
        self.setPower(0);
        for i in range(2):
            time.sleep(0.5)
            self.monitorModbusStatus();
#         if(not self.LoopIfNotMeetReq(self.checkModbusIfInit, 20)):
#             print("checkModbusIfInit doesn't meet the requirement")
#         else:
#             print("checkModbusIfInit pass the test")

        # close the modbus device
        self.instrument.write_register(self.K_op_mode, 0, 0, 6)  # K_op_mode
        
        print("Init job completed")


    def openModbus(self):
        # set up connection: port name, slave address (in decimal)
        self.instrument = minimalmodbus.Instrument(self.USB_Port, self.slaveAddress)  # port name, slave address (in decimal)
        ### We need to do some special writes before sending commands
        ## Set the security register
        self.instrument.write_register(self.security_code, 125, 0, 6)

        # Set the timeout register
        self.instrument.write_register(self.Heartbeat, 333, 0, 6)
        # set the op mode off
        self.instrument.write_register(self.K_op_mode, 0, 0, 6)  # K_op_mode

    def setLimitation(self):
        # set the limitation among current, power, voltage
        self.instrument.write_register(self.bat_max_chrg_crt,self.signedToUnsigned( -100 * self.current_scale), 0, 6);
        self.instrument.write_register(self.bat_max_dischrg_crt, self.signedToUnsigned (100 * self.current_scale), 0, 6);
        # set the charge power limitation
        self.instrument.write_register(self.bat_max_chrg_power, self.signedToUnsigned (30 * self.power_scale), 0, 6)

        ## set Max voltage
        self.instrument.write_register(self.bat_max_volt, self.signedToUnsigned (self.max_vol * self.voltage_scale), 0, 6)
        ## set Min voltage
        self.instrument.write_register(self.bat_min_volt, self.signedToUnsigned (self.min_vol * self.voltage_scale), 0, 6);

    def initCurrent(self):

        requiredCurrent = self.init_current;
        self.instrument.write_register(41026, self.current_mode, 0, 6)  # K_op_mode
        self.instrument.write_register(41027, self.signedToUnsigned(requiredCurrent * self.current_scale), 0, 6)  # Op_mode_setpoint



    def initPower(self):
        requiredPower = self.init_power;
        self.instrument.write_register(self.K_op_mode, self.power_mode, 0, 6)  # K_op_mode
        self.instrument.write_register(self.Op_mode_setpoint,self.signedToUnsigned(requiredPower * self.power_scale), 0, 6)  # Op_mode_setpoint


    # check function
    def LoopIfNotMeetReq(self, handler1, times, *args, **kwargs):

        for i in range(times):
            if (handler1(*args)):
                return True;
        return False;

    def checkModbusIfInit(self):
        DCBusPower = self.instrument.read_register(self.epcl_dc_link_pwr , 0, 4) / self.power_scale;
        DCBusCurrent = self.instrument.read_register(self.epc1_dc_link_crnt , 0, 4) / self.current_scale;
        DCBusVoltage = self.instrument.read_register(self.epcl_dc_link_volt, 0, 4) / self.voltage_scale;
        if (DCBusPower > 0 - self.variance_power and DCBusPower < 0 + self.variance_power and DCBusCurrent > 0 - self.variance_current and DCBusCurrent < 0 + self.variance_current and DCBusVoltage < self.max_vol and DCBusVoltage > self.min_vol):
            print("Current and power are all set nearly 0, meet the requirement")
            return True;
        print("----------------")
        print("DCBusPower: " + str(DCBusPower))
        print("DCBusCurrent: " + str(DCBusCurrent))
        print("DCBusVoltage: " + str(DCBusVoltage))
        str1 = "DCBusPower: " + str(DCBusPower) + ";" + "DCBusCurrent: " + str(DCBusCurrent) + ";" + "DCBusVoltage: " + str(DCBusVoltage) + ";"
        logging.info(str1)
        return False;
        pass;
    
    def monitorModbusStatus(self):
        DCBusPower = self.getPower();
        DCBusCurrent = self.getCurrent();
        DCBusVoltage = self.getVoltage();
        DCref = self.instrument.read_register(30264 , 0, 4) ;
        print("----------------")
        print("DCBusPower: " + str(DCBusPower))
        print("DCBusCurrent: " + str(DCBusCurrent))
        print("DCBusVoltage: " + str(DCBusVoltage))
        print("DCBusRef: " + str(DCref));
        print("DCBusPowerUnsigned: " + str(self.instrument.read_register(self.epcl_dc_link_pwr, 0, 4)))
        print("remote voltage: " + str(self.instrument.read_register(30263, 0, 4)/ self.voltage_scale))
        str1 = "DCBusPower: " + str(DCBusPower) + ";" + "DCBusCurrent: " + str(DCBusCurrent) + ";" + "DCBusVoltage: " + str(DCBusVoltage) + ";"
        logging.info(str1)
    
    def checkIfModbusCurrentRight(self, upLine, bottomLine):
        current = self.getCurrent();
        if (current < upLine and current > bottomLine):
            return True;
        else:
            return False;

    def checkIfModbusVoltageRight(self, upLine, bottomLine):
        voltage = self.getVoltage();
        if (voltage < upLine and voltage > bottomLine):
            return True;
        else:
            return False;

    # get and set function

    def getCurrent(self):
        DCBusCurrent = self.unsignedToSigned(self.instrument.read_register(self.epc1_dc_link_crnt, 0, 4)) / self.current_scale;
        return DCBusCurrent;

    def getPower(self):
        unsigned_power = self.instrument.read_register(self.epcl_dc_link_pwr, 0, 4)
        DCBusPower = self.unsignedToSigned(unsigned_power) / self.power_scale;

        return DCBusPower;

    def getVoltage(self):
        DCBusVoltage = self.unsignedToSigned(self.instrument.read_register(self.epcl_dc_link_volt, 0, 4)) / self.voltage_scale;
        return DCBusVoltage

    def setCurrent(self, value):
        self.instrument.write_register(self.K_op_mode, self.current_mode, 0, 6)  # K_op_mode
        print("SETTING POINTS")
        print(self.signedToUnsigned(value * self.current_scale))
#         self.instrument.write_register(self.Op_mode_setpoint,self.signedToUnsigned( value * self.current_scale ) , 0, 6)  # Op_mode_setpoint
        self.instrument.write_register(self.Op_mode_setpoint,self.signedToUnsigned(value * self.current_scale) , 0, 6)

    def setPower(self, value):
        self.instrument.write_register(self.K_op_mode, self.power_mode, 0, 6) # K_op_mode
        print("power unsigned value " + str(self.signedToUnsigned( value * self.power_scale)))
#         self.instrument.write_register(self.Op_mode_setpoint, 65028, 0, 6) # Op_mode_setpoint
        self.instrument.write_register(self.Op_mode_setpoint, self.signedToUnsigned( value * self.power_scale), 0, 6) # Op_mode_setpoint
        
    def setVoltage(self, value):
        self.instrument.write_register(self.K_op_mode, self.voltage_mode, 0, 6) # K_op_mode
        self.instrument.write_register(self.Op_mode_setpoint,self.signedToUnsigned (value * self.voltage_scale), 0, 6) # Op_mode_setpoint
    def signedToUnsigned(self, signedValue):
        if(signedValue < 0):
            signedValue += 2**16;
        return signedValue;
    def unsignedToSigned(self, unsignedValue):
        if(unsignedValue >= 2**15):
            return unsignedValue - 2**16
        return unsignedValue;

    def __del__(self):
        print("exit the program")
        self.instrument.write_register(41026, 0, 0, 6)  # K_op_mode
        # self.setCurrent(0)
        # # self.setVoltage(0)
        # self.setPower(0)
        pass;
    def close(self):
        self.instrument.write_register(41026, 0, 0, 6)  # K_op_mode

m1 = ModbusHandler();
m1.close();