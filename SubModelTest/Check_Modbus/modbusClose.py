#!/usr/bin/env python3
import minimalmodbus
USB_Port = '/dev/ttyUSB0'
slaveAddress = 2;
security_code = 41024
Heartbeat = 41025
K_op_mode = 41026
        # set up connection: port name, slave address (in decimal)
instrument = minimalmodbus.Instrument(USB_Port, slaveAddress)  # port name, slave address (in decimal)
        ### We need to do some special writes before sending commands
        ## Set the security register
instrument.write_register(security_code, 125, 0, 6)

        # Set the timeout register
instrument.write_register(Heartbeat, 333, 0, 6)
        # set the op mode off
instrument.write_register(K_op_mode, 0, 0, 6)  # K_op_mode