#!/usr/bin/env python3
import minimalmodbus
import time
import csv
import logging

class ModbusHandler:
    def __init__(self):
        logging.basicConfig(filename='Modbus Status.log', level=logging.DEBUG)
        self.USB_Port = '/dev/ttyUSB0'
        self.slaveAddress = 2;
        
        self.current_mode = 1;
        self.power_mode = 2;
        self.voltage_mode = 4
        
        self.max_vol = 384
        self.min_vol = 264
        
        self.set_current_scale = 52.094
        self.read_current_scale = 32.767;
        
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
        
        self.Init();

    def Init(self):
        # set up connection: port name, slave address (in decimal)
        self.instrument = minimalmodbus.Instrument(self.USB_Port, self.slaveAddress)  # port name, slave address (in decimal)
        logging.info("----------------")

#         ## Read voltage set point(Init value) ##
#         self.instrument.write_register(41026, self.voltage_mode, 0, 6)  # K_op_mode
#         voltage = self.instrument.read_register(41027, 0) / self.voltage_scale
#         print("The Initial voltage is ", str(voltage), "Volts")

        ### We need to do some special writes before sending commands
        ## Set the security register
        self.instrument.write_register(self.security_code, 125, 0, 6)

        # Set the timeout register
        self.instrument.write_register(self.Heartbeat, 333, 0, 6)
        # set the op mode off        
        self.instrument.write_register(self.K_op_mode, 0, 0, 6)  # K_op_mode

        # set the current limitation
        self.instrument.write_register(self.bat_max_chrg_crt, 30 * self.set_current_scale, 0, 6);
        self.instrument.write_register(self.bat_max_dischrg_crt, 30 * self.set_current_scale, 0, 6);
        # set the charge power limitation
        self.instrument.write_register(self.bat_max_chrg_power, 20 * self.power_scale, 0, 6)  
        ## set Max voltage
        self.instrument.write_register(self.bat_max_volt, self.max_vol * self.voltage_scale, 0, 6)
        ## set Min voltage
        self.instrument.write_register(self.bat_min_volt, self.min_vol * self.voltage_scale, 0, 6);

        # # set current 0
        logging.info("set current 0")
        requiredCurrent = 2;
        self.instrument.write_register(41026, self.current_mode, 0, 6)  # K_op_mode
        self.instrument.write_register(41027, requiredCurrent * self.set_current_scale, 0, 6)  # Op_mode_setpoint
        
#         logging.info("set power 0")
#         requiredPower = 0.1;
#         self.instrument.write_register(self.K_op_mode, self.power_mode, 0, 6)  # K_op_mode
#         self.instrument.write_register(self.Op_mode_setpoint, requiredPower * self.power_scale, 0, 6)  # Op_mode_setpoint

        
        for i in range(10):
            time.sleep(1);
            if (self.checkModbusIfInit()):
                break;
#         self.LoopIfNotMeetReq(self.checkModbusIfInit(), 100);
        self.instrument.write_register(41026, 0, 0, 6)  # K_op_mode
        
        print("Init job completed")



    def LoopIfNotMeetReq(self, handler, times, *args, **kwargs):
        try:
            for i in range(times):
#                 print("LoopIfNotMeetReq: " + handler.__name__ + ": " + str(i) + " times")
                time.sleep(1);
                if (handler(*args)):
                    return True;
        except:
            print("loop not meet req")
            raise Exception(handler.__name__ + " cannot work even after " + str(times) + " times");
        finally:
            return False;

    def checkModbusIfInit(self):
        DCBusPower = self.instrument.read_register(30266, 0, 4) / self.power_scale;
        DCBusCurrent = self.instrument.read_register(30267, 0, 4) / self.read_current_scale;
        DCBusVoltage = self.instrument.read_register(30265, 0, 4) / self.voltage_scale;
        if (DCBusPower == 0   and DCBusCurrent == 0 and DCBusVoltage < self.max_vol and DCBusVoltage > self.min_vol):
            print("meet the requirement")
            return True;
        print("----------------")
        print("DCBusPower: " + str(DCBusPower))
        print("DCBusCurrent: " + str(DCBusCurrent))
        print("DCBusVoltage: " + str(DCBusVoltage))
        str1 = "DCBusPower: " + str(DCBusPower) + ";" + "DCBusCurrent: " + str(DCBusCurrent) + ";" + "DCBusVoltage: " + str(DCBusVoltage) + ";"
        
        logging.info(str1)
        return False;
        pass;

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

    def getCurrent(self):
        DCBusCurrent = self.instrument.read_register(30267, 0, 4)/ self.read_current_scale;
        return DCBusCurrent;

    def getPower(self):
        DCBusPower = self.instrument.read_register(30266, 0, 4) / self.power_scale;
        return DCBusPower;

    def getVoltage(self):
        DCBusVoltage = self.instrument.read_register(30265, 0, 4) / self.voltage_scale;
        return DCBusVoltage

    def setCurrent(self, value):
        self.instrument.write_register(41026, self.current_mode, 0, 6)  # K_op_mode
        self.instrument.write_register(41027, value * self.set_current_scale, 0, 6)  # Op_mode_setpoint

    def setPower(self, value):
        self.instrument.write_register(41026, self.power_scale, 0, 6) # K_op_mode
        self.instrument.write_register(41027, value * self.power_scale, 0, 6) # Op_mode_setpoint

    def setVoltage(self, value):
        self.instrument.write_register(41026, self.voltage_scale, 0, 6) # K_op_mode
        self.instrument.write_register(41027, value * self.voltage_scale, 0, 6) # Op_mode_setpoint

    def __del__(self):
        print("exit the program")
        self.instrument.write_register(41026, 0, 0, 6)  # K_op_mode
#             self.setCurrent(0)
#             self.setVoltage(0)
#             self.setPower(0)
        pass;
m1 = ModbusHandler();