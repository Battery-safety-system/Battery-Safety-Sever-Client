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

        self.Init();

    def Init(self):

        logging.info("----------------")
        self.openModbus();

        self.setLimitation();

        self.setCurrent(0);

        self.setPower(0)

        if(not self.LoopIfNotMeetReq(self.checkModbusIfInit, 20)):
            print("checkModbusIfInit doesn't meet the requirement")
            self.closeModbus()
            raise Exception("checkModbusIfInit errors")
        # else:
        #     print("checkModbusIfInit pass the test")
        
        self.PreviousTime = time.time();
        # close the modbus device
        # print("ModbusInit job completed")

    def setLimitation(self):
        # set the limitation among current, power, voltage
        self.instrument.write_register(self.bat_max_chrg_crt, self.signedToUnsigned(self.max_crt * self.current_scale), 0, 6);
        self.instrument.write_register(self.bat_max_dischrg_crt, self.signedToUnsigned(self.max_dis_crt * self.current_scale), 0, 6);
        # set the charge power limitation
        self.instrument.write_register(self.bat_max_chrg_power, self.signedToUnsigned(self.max_power * self.power_scale), 0, 6)

        ## set Max voltage
        self.instrument.write_register(self.bat_max_volt, self.signedToUnsigned(self.max_vol * self.voltage_scale), 0,
                                       6)
        ## set Min voltage
        self.instrument.write_register(self.bat_min_volt, self.signedToUnsigned(self.min_vol * self.voltage_scale), 0,
                                       6);

    def checkModbusIfInit(self):
        DCBusPower = self.getPower();
        DCBusCurrent = self.getCurrent()
        RemoteVoltage = self.getVoltage();
        if (
                DCBusPower > 0 - self.variance_power and DCBusPower < 0 + self.variance_power and DCBusCurrent > 0 - self.variance_current and DCBusCurrent < 0 + self.variance_current and RemoteVoltage < self.max_vol and RemoteVoltage > self.min_vol):
            # print("Current and power are all set nearly 0, meet the requirement")
            return True;
        print("----------------")
        print("DCBusPower: " + str(DCBusPower))
        print("DCBusCurrent: " + str(DCBusCurrent))
        print("RemoteVoltage: " + str(RemoteVoltage))
        str1 = "DCBusPower: " + str(DCBusPower) + ";" + "DCBusCurrent: " + str(
            DCBusCurrent) + ";" + "RemoteVoltage: " + str(RemoteVoltage) + ";"
        # logging.info(str1)
        return False;



# -------------------------- Status Function -----------------------------------------

    def setStatusByVoltageInNormalWarningState(self, statusObj):
        assert isinstance(statusObj, Status)
#         volLowWarning = 322
        volLowWarning = 268
        volHighWarning = 384  # test
        volHighDangerous = 390;
        volLowDangerous = 264
        vol = self.info_dict["modbus_Voltage"]
        #
        statusObj.isModbusHighVoltageWarning = False;
        statusObj.isModbusHighVoltageDagnerous = False;
        statusObj.isModbusLowVoltageWarning = False;
        statusObj.isModbusLowVoltageDangerous = False;


        if (abs(vol) <=  volLowWarning and abs(vol) > volLowDangerous):
            logging.warning("Modbus voltage Low violated warning")
            statusObj.isModbusLowVoltageWarning = True;
            statusObj.warning = True;

        if (abs(vol) <= volLowDangerous):
            logging.error("Modbus Voltage Low violated Dangerous")
            statusObj.isModbusLowVoltageDangerous = True;
            statusObj.dangerous = True;

        if (abs(vol) >= volHighWarning and abs(vol) < volHighDangerous):
            logging.warning("Modbus voltage High violated warning")
            statusObj.isModbusHighVoltageWarning = True;
            statusObj.warning = True;

        if (abs(vol) >= volHighDangerous):
            logging.error("Modbus Voltage High violated Dangerous")
            statusObj.isModbusHighVoltageDagnerous = True;
            statusObj.dangerous = True;
        pass




# ---------------------- Main Function -------------------------------------------------
    def updateCurrent(self):
        currentTime = time.time();
        if (currentTime - self.PreviousTime > self.IntervalTime):
            self.intervalCount += 1;
            self.PreviousTime = time.time();
            # get the current value we need
            currentVal = self.currentVal * self.CurrentList[self.intervalCount % len(self.CurrentList)]
            # set the current value
            self.setCurrent(currentVal);
            # check if the real value is one the range of expected values
            self.LoopIfNotMeetReq(self.checkIfModbusCurrentRight, 20, currentVal - self.variance_current,
                                  currentVal + self.variance_current)

    def updatePower(self):
        currentTime = time.time();
        if (currentTime - self.PreviousTime > self.IntervalTime):
            self.intervalCount += 1;
            self.PreviousTime = time.time();
            # get the current value we need
            powerVal = self.powerValue * self.PowerList[self.intervalCount % len(self.PowerList)]
            # set the current value
            self.setPower(powerVal);
            # check if the real value is one the range of expected values
            self.LoopIfNotMeetReq(self.checkIfModbusPowerRight, 20, powerVal - self.variance_power,
                                  powerVal + self.variance_power)


    def run(self):
        if self.ControlMode == self.currentControlMode:
            self.updateCurrent();
        elif self.ControlMode == self.powerControlMode:
            self.updatePower()


    def getLabels(self):
        return self.label_list;

    def getDatas(self):
        DCBusPower = self.getPower();
        DCBusCurrent = self.getCurrent();
        RemoteVoltage = self.getVoltage();

        data_list = [DCBusPower, DCBusCurrent, RemoteVoltage]
        self.data_list = data_list;
        self.info_dict["modbus_Power"] = DCBusPower; self.info_dict["modbus_Current"] = DCBusCurrent; self.info_dict["modbus_Voltage"] = RemoteVoltage;
        self.info_dict["remoteVoltage"] = RemoteVoltage
        print("ModbusHandler" + str(self.info_dict))
        return self.data_list;

    def setModbusDischarge(self):
        print("set the modbus to discharge")
        if self.ControlMode == self.currentControlMode:
            currentVal = self.currentVal;
            self.setCurrent(currentVal);
        elif self.ControlMode == self.powerControlMode:
            powerVal = self.powerValue
            self.setPower(powerVal)


    def setModbusCharge(self):
        if self.ControlMode == self.currentControlMode:
            currentVal = -1 * self.currentVal;
            self.setCurrent(currentVal);
        elif self.ControlMode == self.powerControlMode:
            powerVal = -1 * self.powerValue
            self.setPower(powerVal)

        pass


# -------------------------------- Modbus Tools Function ----------------------------

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


# ------------------------------------- get Function -----------------------------------------------

    def getCurrent(self):
        DCBusCurrent = self.unsignedToSigned(
            self.instrument.read_register(self.epc1_dc_link_crnt, 0, 4)) / self.current_scale;
        return DCBusCurrent;

    def getPower(self):
        unsigned_power = self.instrument.read_register(self.epcl_dc_link_pwr, 0, 4)
        DCBusPower = self.unsignedToSigned(unsigned_power) / self.power_scale;

        return DCBusPower;

    def getVoltage(self):
        RemoteVoltage = (self.instrument.read_register(30263, 0, 4) / self.voltage_scale)
        return RemoteVoltage;
    # def getRemoteVoltage(self):
    #     RemoteVoltage = (self.instrument.read_register(30263, 0, 4) / self.voltage_scale)
    #     return RemoteVoltage;

# ---------------------------------------- set Function -------------------------------------------
    def setCurrent(self, value):
        self.instrument.write_register(self.K_op_mode, self.current_mode, 0, 6)  # K_op_mode
        print("SETTING POINTS")
        print(self.signedToUnsigned(value * self.current_scale))
        #         self.instrument.write_register(self.Op_mode_setpoint,self.signedToUnsigned( value * self.current_scale ) , 0, 6)  # Op_mode_setpoint
        self.instrument.write_register(self.Op_mode_setpoint, self.signedToUnsigned(value * self.current_scale), 0, 6)

    def setPower(self, value):
        self.instrument.write_register(self.K_op_mode, self.power_mode, 0, 6)  # K_op_mode
        print("power unsigned value " + str(self.signedToUnsigned(value * self.power_scale)))
        #         self.instrument.write_register(self.Op_mode_setpoint, 65028, 0, 6) # Op_mode_setpoint
        self.instrument.write_register(self.Op_mode_setpoint, self.signedToUnsigned(value * self.power_scale), 0,
                                       6)  # Op_mode_setpoint

    def setVoltage(self, value):
        self.instrument.write_register(self.K_op_mode, self.voltage_mode, 0, 6)  # K_op_mode
        self.instrument.write_register(self.Op_mode_setpoint, self.signedToUnsigned(value * self.voltage_scale), 0,
                                       6)  # Op_mode_setpoint

# ------------------------------------ Data Handler Function ------------------------------------
    def signedToUnsigned(self, signedValue):
        if (signedValue < 0):
            signedValue += 2 ** 16;
        return signedValue;

    def unsignedToSigned(self, unsignedValue):
        if (unsignedValue >= 2 ** 15):
            return unsignedValue - 2 ** 16
        return unsignedValue;

# ----------------------------- Check Function ----------------------------------------

    # check function
    def LoopIfNotMeetReq(self, handler1, times, *args, **kwargs):

        for i in range(times):
            if (handler1(*args)):
                return True;
        return False;



    def monitorModbusStatus(self):
        DCBusPower = self.getPower();
        DCBusCurrent = self.getCurrent();
        RemoteVoltage = self.getVoltage();
        DCref = self.instrument.read_register(30264, 0, 4);
        print("----------------")
        print("DCBusPower: " + str(DCBusPower))
        print("DCBusCurrent: " + str(DCBusCurrent))
        print("RemoteVoltage: " + str(RemoteVoltage))
        print("DCBusRef: " + str(DCref));
        print("DCBusPowerUnsigned: " + str(self.instrument.read_register(self.epcl_dc_link_pwr, 0, 4)))
#         print("remote voltage: " + str(self.instrument.read_register(30263, 0, 4) / self.voltage_scale))
        str1 = "DCBusPower: " + str(DCBusPower) + ";" + "DCBusCurrent: " + str(
            DCBusCurrent) + ";" + "RemoteVoltage: " + str(RemoteVoltage) + ";"
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
    
    def checkIfModbusPowerRight(self, upLine, bottomLine):
        voltage = self.getVoltage();
        if (voltage < upLine and voltage > bottomLine):
            return True;
        else:
            return False;

    def checkIfModbusVoltageInit(self):
        vol = self.info_dict["modbus_Voltage"]

        if (self.checkIfModbusVoltageRight(vol, 0 - self.variance_voltage, 0 + self.variance_voltage)):
            return True;
        else:
            return False;

    # def checkIfModbusLabels(self):






    def __del__(self):
        print("exit the program")
        try:
            self.instrument.write_register(41026, 0, 0, 6)  # K_op_mode
        except:
            print("Modbus Delete: Cannot close Modbus")
