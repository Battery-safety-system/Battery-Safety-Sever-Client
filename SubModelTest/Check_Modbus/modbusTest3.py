#!/usr/bin/env python3
import minimalmodbus
import time

## Simple demo of reading Rhombus PCS data with Python3 and minimalmodbus

# set the variable
USB_Port = '/dev/ttyUSB0'
current_mode = 1;
power_mode = 2;
max_vol = 384
min_vol = 264
set_current_scale = 52.094
read_current_scale = 32.767;
voltage_scale = 32.767
power_scale = 218.44



# set up connection: port name, slave address (in decimal)
instrument = minimalmodbus.Instrument(USB_Port, 2)  # port name, slave address (in decimal)

voltage = instrument.read_register(41027, 0) / voltage_scale
print("The Initial voltage is " , str(voltage), "Volts")

### We need to do some special writes before sending commands
## Set the security register
instrument.write_register(41024, 125, 0, 6)

# Set the timeout register
instrument.write_register(41025, 333, 0, 6)

# Change voltage setpoint (SP) ##

## set Max voltage
instrument.write_register(41028, max_vol * voltage_scale, 0, 6)
## set Min voltage
instrument.write_register(41029, min_vol * voltage_scale, 0, 6);

# section 1 set AC DC value
requiredCurrent = 0;
requiredPower = 0;
# set current 0
instrument.write_register(41026, current_mode, 0, 6) # K_op_mode
instrument.write_register(41027, requiredCurrent * set_current_scale, 0, 6) # Op_mode_setpoint


# check if the current is 0 and voltage meet the requirement;


def LoopIfNotMeetReq( handler, times, *args, **kwargs):
    try:
        for i in range(times):
            time.sleep(1);
            if (handler(*args)):
                return True;
    except:
        raise Exception(handler.__name__ + " cannot work even after " + str(times) + " times");
    finally:
        return False;

def checkModbusIfInit():
    DCBusPower = instrument.read_register(30266, 0, 4) / power_scale;
    DCBusCurrent = instrument.read_register(30267, 0, 4) / set_current_scale;
    DCBusVoltage = instrument.read_register(30265, 0, 4) / voltage_scale;
    if(DCBusPower == 0 and DCBusCurrent == 0 and DCBusVoltage < max_vol and DCBusVoltage > min_vol):
        return True;
    pass;

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

# def checkModbusCurrentIfRight(upLine, bottomLine):
#     DCBusCurrent = instrument.read_register(30267, 0, 4) / current_scale;
#     DCBusVoltage = instrument.read_register(30265, 0, 4) / voltage_scale;
#     if( and DCBusVoltage < 384 and DCBusVoltage > 264):
#         return True;

if(not LoopIfNotMeetReq(checkModbusIfInit, times = 10)):
    exit()


# Section 3: loop work
# set power points and current points on modbus:
requiredCurrent = 3;
error_current = 0.2;
# requiredPower = 0;
# set current xx
instrument.write_register(41026, current_mode, 0, 6) # K_op_mode
instrument.write_register(41027, requiredCurrent * set_current_scale, 0, 6) # Op_mode_setpoint
LoopIfNotMeetReq(checkIfModbusCurrentRight, 3, requiredCurrent + error_current, requiredCurrent - error_current );

# # set power xx
# instrument.write_register(41026, power_mode, 0, 6) # K_op_mode
# instrument.write_register(41027, requiredPower * power_scale, 0, 6) # Op_mode_setpoint


# Section: check all the DC status information
# get DC modbus status information
BatteryRemoteVoltage = instrument.read_register(30263, 0, 4) /
DCLinkSetpoints = instrument.read_register(30264, 0, 4);
DCBusVoltage = instrument.read_register(30265, 0, 4);
DCBusPower = instrument.read_register(30266, 0, 4);
DCBusCurrent = instrument.read_register(30267, 0, 4);
PowerLimit = instrument.read_register(30285, 0, 4);