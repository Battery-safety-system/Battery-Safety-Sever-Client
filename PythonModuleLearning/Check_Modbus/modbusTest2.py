#!/usr/bin/env python3
import minimalmodbus

## Simple demo of reading Rhombus PCS data with Python3 and minimalmodbus

# port name, slave address (in decimal)
instrument = minimalmodbus.Instrument('COM3', 2)

## Read voltage set point ##
# Registernumber, number of decimals
voltage = instrument.read_register(41027, 0) / 32.767
print(voltage, "Volts")

## Read the maximum charge power setpoint
max_charge_power = instrument.read_register(41032,0)
print(max_charge_power)

# using the optional parameter = 4 for read input
DC_volts = instrument.read_register(30265, 0, 4) / 32.767
print(DC_volts, "V DC bus")

### We need to do some special writes before sending commands
## Set the security register
instrument.write_register(41024, 125, 0, 6)
## Set the timeout register
#instrument.write_register(41025, 333, 0, 6)


## Change voltage setpoint (SP) ##
NEW_VOLT = 650
# Registernumber, value, number of decimals for storage
## this works, but need to know what you're doing
#instrument.write_register(41027, NEW_VOLT * 32.767, 0, 6)