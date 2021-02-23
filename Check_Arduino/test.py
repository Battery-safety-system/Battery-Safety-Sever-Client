import serial  # Importing the serial library to communicate with Arduino
import time;

ser = serial.Serial('COM7')
while True:

        # Reading and storing the data coming from Arduino
        # Temp1 = int.from_bytes(ser.read(), "big")

        ####
        # Data = ser.readline();
        # print(Data)
        # print("end")

        ## interface
        PumpFan = '1'; Relay1 = '0'; Relay2 = '1'; PrechargeRelay = '0';

        msg = 'ab'
        # print("start")
        ser.write(msg.encode())
        print("end")
        Data = ser.readline()
        print(Data)

        ###
        # ser.write('1')  # write a string
        # line = ser.readline();
        # print(line);







