import minimalmodbus
USB_Port = '/dev/ttyUSB1'
instrument = minimalmodbus.Instrument(USB_Port, 2)  # port name, slave address (in decimal)

# Go to security code register #41025 and enter the number 125.
instrument.write_register(41024, 125, 1) #

#  heart beat counter is located at address #41027.
instrument.write_register(41025, 333, 1) #

# set the limited time

temperature = instrument.read_register(289, 1)
print(temperature)

## Change temperature setpoint (SP) ##
NEW_TEMPERATURE = 95



instrument.address                         # this is the slave address number
instrument.mode = minimalmodbus.MODE_RTU   # rtu or ascii mode
instrument.clear_buffers_before_each_transaction = True