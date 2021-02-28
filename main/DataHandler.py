


#!/usr/bin/python3
import time
import can
import RPi.GPIO as GPIO
import cantools
import os
import csv
import socket
import pickle
import logging
from File import File
from PcanConnection import PcanConnection
from Message import Message
from PCConnection import PCConnection
from Status import Status
from GPIOHandler import GPIOHandler
from DataHandler import DataHandler

class DataHandler(object):
    """docstring for DataHandler"""
    def __init__(self):
        super(DataHandler, self).__init__()
    

    def handleData(self, messageObj):
        print("Begin handleData()");
        message_data_dict = {} # {BMU01_MAXTemp: xxx, BMU01_MinTemp: xxx, ...}
        message_data_list = []; # date, time, BMU01_MAXTemp, BMU01_MinTemp, ... (based on the label)
        for label in messageObj.label_list: # BMU01_pdo1, BMU01_pdo2
            A_message = messageObj.message_dict[label];
            battery_name = label[0:5] #BMU01 or BMU02
            data_decode = messageObj.db.decode_message(A_message.arbitration_id, A_message.data);
            for key, value in data_decode.items(): # key: Max_temp
                final_label = battery_name + '_' + key;
                message_data_dict[final_label] = value;

        for label in messageObj.final_label_list:
            if(label == 'date'):
                message_data_list.append(time.strftime('%d-%m-%Y'));
            elif(label == 'time'):
                message_data_list.append(time.strftime('%H:%M:%S'));
            else:
                assert label in message_data_dict;
                value = message_data_dict[label];
                message_data_list.append(value);
        # print("message data has been handle, start to send the message data")
        messageObj.message_data_dict = message_data_dict;
        messageObj.message_data_list = message_data_list;
        print("handleData() end")


    def detectVoltage(self, status, messageObj):
        isvolLimited = False;
        for battery in messageObj.battery_list:
            battery_str = 'BMU'+str(battery).zfill(2)
            label = battery_str + '_' + 'CMA_Voltage';
            CMA_Voltage = messageObj.message_data_dict[label];
            if CMA_Voltage >= 48 or CMA_Voltage <= 33:
                isvolLimited = True;
        
        status.isvolLimited = isvolLimited;


    def detectTemp(self, status, messageObj):
        istempHigh = False; 
        for battery in messageObj.battery_list:
            battery_str = 'BMU'+str(battery).zfill(2)
            label = battery_str + '_' + 'CMA_Max_Temp';
            CMA_Max_Temp = messageObj.message_data_dict[label];
            if CMA_Max_Temp >= 35:  ##40?
                status.temperature_voliated_battery.append(battery);
        for battery in status.temperature_voliated_battery:
            battery_str = 'BMU'+str(battery).zfill(2)
            battery_str = battery_str + '_' + 'CMA_Max_Temp';
            CMA_Max_Temp = messageObj.message_data_dict[label];
            if CMA_Max_Temp <= 30:  ##40?
                status.temperature_voliated_battery.remove(battery);
            if not status.temperature_voliated_battery:
                istempHigh = False;
            else: 
                istempHigh = True;
        status.istempHigh = istempHigh;


    def detectCellVoltageViolated(self, status, messageObj):
        isCVViolated = False;
        for battery in messageObj.battery_list:
            battery_str = 'BMU'+str(battery).zfill(2);
            label = battery_str + '_' + 'Max_Cell_Voltage'
            Max_Cell_Voltage = messageObj.message_data_dict[label];
            label = battery_str + '_' + 'Min_Cell_Voltage'
            Min_Cell_Voltage = messageObj.message_data_dict[label];
            if Max_Cell_Voltage >= 4.1 or Min_Cell_Voltage < 2.8:  ##40?
                isCVViolated = True;

        status.isCVViolated = isCVViolated;

    def detectStatus(self, status, messageObj):
        print("Begin to detect the status")
        self.detectVoltage(status, messageObj);
        self.detectTemp(status, messageObj);
        self.detectCellVoltageViolated(status, messageObj);
        print("is there any voltage violate: %s; is the temperature too high: %s;" %(status.isvolLimited, status.istempHigh ))
        print("detectStatus End")
        