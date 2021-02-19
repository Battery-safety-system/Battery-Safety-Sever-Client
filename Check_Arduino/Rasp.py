import serial  # Importing the serial library to communicate with Arduino

ser = serial.Serial('/dev/ttyACM1', 9600)
while True:
    try:
        if ser.readline() != "Arduino: Prepare for Arduino Communication":
            pass # Expception
        ser.write('Rasp: I\'m OK');
        # step1: receive the mapstatus
        mapstatus = ser.readline();

        # handle mapstatus
        controlSig = "";
        # step2:
        ser.write(controlSig);
        if ser.readline() != "Arduino: Received Control Map":
            pass # Exception



    except KeyboardInterrupt:
        pass;

# write the step:
# preparation:
# function:
# step
# 1. serial receive the mapstatus
# 2. handle the mapstatus
# 3. Serial output the control status
#