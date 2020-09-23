#!/usr/bin/python3
import time
import can
import RPi.GPIO as GPIO
import cantools
import os

import socket
import pickle
### set the Pump Relay pins Pump: 18 Relay: 16
Pump=18;
Relay=16;
GPIO.setwarnings(False)
GPIO.setmode(GPIO.BCM)
GPIO.setup(Pump, GPIO.OUT)
GPIO.setup(Relay, GPIO.OUT)
GPIO.output(Relay, GPIO.HIGH);
GPIO.output(Pump, GPIO.LOW);

## bus set up
bustype = 'socketcan'
channel = 'can0'
bus = can.interface.Bus(channel=channel, bustype=bustype)

### sync message setting
db=cantools.database.load_file('Goodwood_15BMUs_IFSpecV3_Node.dbc');
sync_message=db.get_message_by_name('SYNC');
sync_data=sync_message.encode({'Sync_Count':0xFF});
send_message = can.Message(arbitration_id=0x80, data=sync_data,extended_id=False)

ip_addre='192.168.137.1'
client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client.connect((ip_addre, 6689))

tempHigh=False;

if __name__ == '__main__':
    try:
        
        while True:
            print("start")
            print(time.strftime('%H-%M-%S'))
            ### send the sync message
            bus.send(send_message);

            ### init
            message_list=[];
            new_message_list=[];
            message_dict={}

            # receive all the message I need
            while True:
                message = bus.recv()
                if(message.arbitration_id==0x181): # BMU01_pdo1 battery 1-pdo1
                    message_dict[1]=message;
                elif(message.arbitration_id==0x183): # BMU01_pdo1 battery 2-pdo1
                    message_dict[2]=message;
                elif(message.arbitration_id==0x381): # BMU01_pdo3 battery 1-pdo3
                    message_dict[3]=message
                elif(message.arbitration_id==0x481): # BMU01_pdo4 battery 1-pdo4
                    message_dict[4]=message
                elif(message.arbitration_id==0x383): #  BMU01_pdo3 battery 2-pdo3
                    message_dict[5]=message
                elif(message.arbitration_id==0x483): # BMU01_pdo3 battery 2-pdo4
                    message_dict[6]=message

                if(len(message_dict)==6): ## the number of message
                    break;

            ## add the data to the specific list
            # init
            battery_number=2
            cvs_list=[];
            CMA_Max_Temp_list=[];
            CMA_Voltage_list=[];
            voltage_list=[]
            voltage_list2=[]

            #
            for i in range(len(message_dict)):
                message_list.append(message_dict[i+1]);
                message=message_dict[i+1];
                if(i<battery_number):
                    data_decode=db.decode_message(message.arbitration_id, message.data)
                    CMA_Max_Temp=data_decode['CMA_Max_Temp'];
                    CMA_Voltage=data_decode['CMA_Voltage'];
                    cvs_list.append(CMA_Max_Temp);cvs_list.append(CMA_Voltage);
                    CMA_Max_Temp_list.append(CMA_Max_Temp);
                    CMA_Voltage_list.append(CMA_Voltage);
                elif(i==2):
                    data_decode=db.decode_message(message.arbitration_id, message.data)
                    for i in range(8):
                        num=i+1
                        label="Cell_"+str(num)+"_Voltage";
                        Cell_Voltage=data_decode[label];
                        voltage_list.append(Cell_Voltage);

                elif(i==3):
                    data_decode=db.decode_message(message.arbitration_id, message.data)
                    for i in range(8,12):
                        num=i+1
                        label="Cell_"+str(num)+"_Voltage";
                        Cell_Voltage=data_decode[label];
                        voltage_list.append(Cell_Voltage);

                elif(i==4):
                    data_decode=db.decode_message(message.arbitration_id, message.data)
                    for i in range(8):
                        num=i+1
                        label="Cell_"+str(num)+"_Voltage";
                        Cell_Voltage=data_decode[label];
                        voltage_list2.append(Cell_Voltage);

                elif(i==5):
                    data_decode=db.decode_message(message.arbitration_id, message.data)
                    for i in range(8,12):
                        num=i+1
                        label="Cell_"+str(num)+"_Voltage";
                        Cell_Voltage=data_decode[label];
                        voltage_list2.append(Cell_Voltage);

                    ### Relay and Pump logic judgement
        ##
            
            volLimited=False;
            ### check every temp, if higher than 40, pump start
            for CMA_Max_Temp in CMA_Max_Temp_list :
                if CMA_Max_Temp >= 35:##40?
                    tempHigh=True;
                    break;
                elif CMA_Max_Temp<=30:
                    tempHigh=False;

            ### check every voltage: if voltage violated, the relay start and the code finish
            for CMA_Voltage in CMA_Voltage_list:
                if CMA_Voltage >= 48 or CMA_Voltage <= 33:  ## 33 48?
            ## set relay GPIO low
                    volLimited=True;
                    print("relayoff")
                    break;
                
                
            
            cvs_list.append(tempHigh)
            cvs_list.append(volLimited)
            
                        # create a socket and send data

            voltage_list.extend(voltage_list2)
            cvs_list =pickle.dumps(cvs_list)
            voltage_list=pickle.dumps(voltage_list)
            #
            

            if(tempHigh==True):
            ## set the pump GPIO high
                GPIO.output(Pump, GPIO.HIGH)
                print("do that")
                time.sleep(4)
                continue;
            else:
                GPIO.output(Pump, GPIO.LOW)

            if(volLimited==True):
                GPIO.output(Relay, GPIO.LOW);
                break;
            else:
                GPIO.output(Relay, GPIO.HIGH);
            
            time.sleep(4)
            print("handle problem")
            try:
                client.settimeout(8)
                client.send(cvs_list)
                print("has send")
                rec_data = client.recv(1024)
                client.settimeout(None)
                print(b'form server receive:' + rec_data)
                
                client.settimeout(8)
                client.send(voltage_list)
                print("has send")
                rec_data = client.recv(1024)
                client.settimeout(None)
                print(b'form server receive:' + rec_data)
                
            except Exception as e:
                print(e)
                client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                try:
                    client.settimeout(4)
                    client.connect((ip_addre, 6689))
                except Exception as e:
                    print(e)
                    client.settimeout(None)
            print("finis\n")
            ### wait for 4 seconds
            
    except ValueError:
        client.close()
        print(ValueError)
