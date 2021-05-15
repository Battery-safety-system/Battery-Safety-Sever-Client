#!/usr/bin/python3
import time
import can
import RPi.GPIO as GPIO
import csv
import cantools
import os
# Init
bustype = 'socketcan'
channel = 'can0'
bus = can.interface.Bus(channel=channel, bustype=bustype)

db=cantools.database.load_file('Goodwood_15BMUs_IFSpecV3_Node.dbc');
sync_message=db.get_message_by_name('SYNC');
sync_data=sync_message.encode({'Sync_Count':0xFF});
send_message = can.Message(arbitration_id=0x80, data=sync_data,extended_id=False)


### send the sync message


### Receive message and grab data from it
message_dict={}
while True:
	bus.send(send_message);
	message = bus.recv()
	### for example 
	if message.arbitration_id == 0x181:
		data_decode=db.decode_message(message.arbitration_id, message.data)
		# check the db file and find there is CMA_Max_Temp, CMA_Voltage, etc.
		CMA_Max_Temp=data_decode['CMA_Max_Temp'];
        CMA_Voltage=data_decode['CMA_Voltage'];
        cvs_list.append(CMA_Max_Temp);cvs_list.append(CMA_Voltage);
        CMA_Max_Temp_list.append(CMA_Max_Temp);
        CMA_Voltage_list.append(CMA_Voltage);

	pass
