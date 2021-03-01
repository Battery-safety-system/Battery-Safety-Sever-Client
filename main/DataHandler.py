


#!/usr/bin/python3
import time
import can
import RPi.GPIO as GPIO
import cantools
import os


class DataHandler(object):
    """docstring for DataHandler"""
    def __init__(self):
        super(DataHandler, self).__init__()
        print("Initializae Data Handler")
    

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
            if(label == 'istempHigh' or label == 'isvolLimited' or label == 'isCVViolated'):
                pass;
            elif(label == 'date'):
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
            if CMA_Max_Temp >= 40:  ##40?
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
        print(messageObj.message_data_dict)
        print("is there any voltage violated: %s; is the temperature too high: %s;is there any cell voltage violated: %s" %(status.isvolLimited, status.istempHigh, status.isCVViolated))
        print("detectStatus End")
        
    def setStatusToMessageObj(self, StatusObj, MessageObj):
        MessageObj.message_data_list.append(StatusObj.istempHigh);
        MessageObj.message_data_list.append(StatusObj.isvolLimited);
        MessageObj.message_data_list.append(StatusObj.isCVViolated);
    
    
    def judgeGPIOInfo(self, StatusObj):
        GPIOInfoList = [];
        if(StatusObj.istempHigh == True):
            GPIOInfoList.append({"device": "Pump", "pin_number": 18, "pin_type": GPIO.OUT, "pin_value": GPIO.HIGH});
            print("temperature is too high, the pump continue to work");
        else:
            print("temp is in control, the pump is off")
            GPIOInfoList.append({"device": "Pump", "pin_number": 18, "pin_type": GPIO.OUT, "pin_value": GPIO.LOW});

        if(StatusObj.isvolLimited == True or StatusObj.isCVViolated ):
            GPIOInfoList.append({"device": "Relay", "pin_number": 16, "pin_type": GPIO.OUT, "pin_value": GPIO.LOW});
            print("voltage is out of control, relay is off")

        else:
            GPIOInfoList.append({"device": "Relay", "pin_number": 16, "pin_type": GPIO.OUT, "pin_value": GPIO.HIGH});
            print("voltage is in control, the relay is on")
        return GPIOInfoList;
    
    
    def getGPIOInitInfoList(self):
        GPIOInfoList = []
        GPIOInfoList.append({"device": "Pump", "pin_number": 18, "pin_type": GPIO.OUT, "pin_value": GPIO.LOW});
        GPIOInfoList.append({"device": "Relay", "pin_number": 16, "pin_type": GPIO.OUT, "pin_value": GPIO.HIGH});
        return GPIOInfoList

    def getStatusList(self, StatusObj):
        return [StatusObj.isvolLimited, StatusObj.istempHigh, StatusObj.isCVViolated]

    def storeToLocalRepo(self, FileObj, MessageObj):
        FileObj.WritetoCVS(MessageObj.message_data_list, MessageObj.final_label_list);
        pass

    def activateDevice(self, GPIOInfoList):
        print("activateDevice() begin")
        for GPIOInfo in GPIOInfoList:
            GPIO.output(GPIOInfo["pin_number"], GPIOInfo["pin_value"]);
        print("activateDevice() end")
