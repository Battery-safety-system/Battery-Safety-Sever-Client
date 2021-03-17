import minimalmodbus
import time
# open the minimalmodbus device
USB_Port = '/dev/ttyUSB1'
instrument = minimalmodbus.Instrument(USB_Port, 2)  # port name, slave address (in decimal)

# Go to security code register #41025 and enter the number 125.
instrument.write_register(41024, 125, 1) #

#  heart beat counter is located at address #41027.
instrument.write_register(41025, 333, 1) #

# section 1 set AC DC value
requiredCurrent = 0;
requiredPower = 0;
# set current 0
instrument.write_register(41026, 1, 1) # K_op_mode
instrument.write_register(41027, 0, 1) # Op_mode_setpoint

# # set power 0
# instrument.write_register(41026, 2, 1) # K_op_mode
# instrument.write_register(41027, 0, 1) # Op_mode_setpoint
#

# section 2 check
## Check if the grid trip timings and limits registers (41033 - 41045) are set as required.

## modbus to check if the power is 0
times = 10;
def LoopIfNotMeetReq(handler, times):

    for i in range(times):
        time.sleep(1);
        if(handler()):
            return True;
    return False;

def checkModbusPowerIfInit():
    DCBusPower = instrument.read_register(30266);
    DCBusCurrent = instrument.read_register(30267);
    DCBusVoltage = instrument.read_register(30265);
    if(DCBusPower == 0 and DCBusCurrent == 0 and DCBusVoltage < 384 and DCBusVoltage > 264):
        return True;

    pass;

def checkModbusCurrentIfRight():
    pass
##
if(not LoopIfNotMeetReq(checkModbusPowerIfInit, 10)):
    exit()

# Section 3: loop work
# set power points and current points on modbus:
requiredCurrent = 3;
# requiredPower = 0;
# set current xx
instrument.write_register(41026, 1, 1) # K_op_mode
instrument.write_register(41027, requiredCurrent, 1) # Op_mode_setpoint
LoopIfNotMeetReq(checkModbusCurrentIfRight, 3);

# # set power xx
# instrument.write_register(41026, 2, 1) # K_op_mode
# instrument.write_register(41027, requiredPower, 1) # Op_mode_setpoint



# get DC modbus status information
BatteryRemoteVoltage = instrument.read_register(30263)
DCLinkSetpoints = instrument.read_register(30264);
DCBusVoltage = instrument.read_register(30265);
DCBusPower = instrument.read_register(30266);
DCBusCurrent = instrument.read_register(30267);
PowerLimit = instrument.read_register(30285);



#
#
# instrument.address                         # this is the slave address number
# instrument.mode = minimalmodbus.MODE_RTU   # rtu or ascii mode
# instrument.clear_buffers_before_each_transaction = True
# # ref: https://minimalmodbus.readthedocs.io/en/stable/usage.html


