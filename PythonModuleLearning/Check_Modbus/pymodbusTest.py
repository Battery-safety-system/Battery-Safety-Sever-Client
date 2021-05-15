from pymodbus.client.sync import ModbusSerialClient

client = ModbusSerialClient(
    method='rtu',
    port='/dev/ttyUSB0',
    baudrate=19200,
    timeout=3,
    parity='N',
    stopbits=1,
    bytesize=8
)

UNIT = 0x1
if client.connect():  # Trying for connect to Modbus Server/Slave
    '''Reading from a holding register with the below content.'''
    print("connect")
#     res = client.read_holding_registers(address=1, count=1, unit=1)
    client.write_register(41024, 125)
    '''Reading from a discrete register with the below content.'''
    # res = client.read_discrete_inputs(address=1, count=1, unit=1)
    client.write_register(41025, 333) #
    client.write_register(41026, 1) # K_op_mode
    client.write_register(41027, 0) # Op_mode_setpoint
    print("get it")
    BatteryRemoteVoltage = client.read_input_registers(2, 30263)
    print("get it")
#     print(BatteryRemoteVoltage)
#     if not rq.isError():
#         print(rq.registers)
#     else:
#         print(rq)

else:
    print('Cannot connect to the Modbus Server/Slave')