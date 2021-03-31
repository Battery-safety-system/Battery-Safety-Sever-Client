# !/usr/bin/python3
import time
import can
import RPi.GPIO as GPIO
import cantools
import os


class DataHandler(object):
    """docstring for DataHandler"""

    def __init__(self):
        super(DataHandler, self).__init__()
        print("Initializae Client Data Handler")

    def handleData(self, messageObj):
        print("Begin handleData()");
        message_data_dict = {}  # {BMU01_MAXTemp: xxx, BMU01_MinTemp: xxx, ...}
        message_data_list = [];  # date, time, BMU01_MAXTemp, BMU01_MinTemp, ... (based on the label)
        for label in messageObj.label_list:  # BMU01_pdo1, BMU01_pdo2
            A_message = messageObj.message_dict[label];
            battery_name = label[0:5]  # BMU01 or BMU02
            data_decode = messageObj.db.decode_message(A_message.arbitration_id, A_message.data);
            for key, value in data_decode.items():  # key: Max_temp
                final_label = battery_name + '_' + key;
                message_data_dict[final_label] = value;

        for label in messageObj.final_label_list:
            if (label == 'istempHigh' or label == 'isvolLimited' or label == 'isCVViolated'):
                pass;
            elif (label == 'date'):
                message_data_list.append(time.strftime('%d-%m-%Y'));
            elif (label == 'time'):
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
            battery_str = 'BMU' + str(battery).zfill(2)
            label = battery_str + '_' + 'CMA_Voltage';
            CMA_Voltage = messageObj.message_data_dict[label];
            if CMA_Voltage >= 48 or CMA_Voltage <= 33:
                isvolLimited = True;

        status.isCMAVolVio = isvolLimited;

    def detectTemp(self, status, messageObj):
        istempHigh = False;
        for battery in messageObj.battery_list:
            battery_str = 'BMU' + str(battery).zfill(2)
            label = battery_str + '_' + 'CMA_Max_Temp';
            CMA_Max_Temp = messageObj.message_data_dict[label];
            if CMA_Max_Temp >= 40:  ##40?
                status.temperature_voliated_battery.append(battery);
        for battery in status.temperature_voliated_battery:
            battery_str = 'BMU' + str(battery).zfill(2)
            label = battery_str + '_' + 'CMA_Max_Temp';
            CMA_Max_Temp = messageObj.message_data_dict[label];
            if CMA_Max_Temp <= 30:  ##40?
                status.temperature_voliated_battery.remove(battery);
            if not status.temperature_voliated_battery:
                istempHigh = False;
            else:
                istempHigh = True;
        status.isCMATempVio = istempHigh;

    def detectCellVoltageViolated(self, status, messageObj):
        isCVViolated = False;
        for battery in messageObj.battery_list:
            Max_Cell_Voltage = -1;
            Min_Cell_Voltage = 1000;
            battery_str = 'BMU' + str(battery).zfill(2);
            for i in range(1, 12):
                label = battery_str + '_' + 'Cell' + '_' + str(i) + '_Voltage'
                if(messageObj.message_data_dict[label] > Max_Cell_Voltage) :
                    Max_Cell_Voltage = messageObj.message_data_dict[label]
                if(messageObj.message_data_dict[label] < Min_Cell_Voltage ):
                    Min_Cell_Voltage = messageObj.message_data_dict[label];
            print("Max_Cell_Voltage: " + str(Max_Cell_Voltage));
            print("Min_Cell_voltage: " + str(Min_Cell_Voltage))
            if Max_Cell_Voltage >= 4.1 or Min_Cell_Voltage < 2.8:  ##40?
                isCVViolated = True;
        print("is Cell Voltage Violated: " + str(isCVViolated))
        status.isCellVolVio = isCVViolated;

    def detectStatus(self, status, messageObj):
        print("Begin to detect the status")
        self.detectVoltage(status, messageObj);
        self.detectTemp(status, messageObj);
        self.detectCellVoltageViolated(status, messageObj);
        print(messageObj.message_data_dict)
        print(
            "is there any voltage violated: %s; is the temperature too high: %s;is there any cell voltage violated: %s" % (
                status.isCMAVolVio, status.isCMATempVio, status.isCellVolVio))
        print("detectStatus End")

    def setStatusToMessageObj(self, StatusObj, MessageObj):
        MessageObj.message_data_list.append(StatusObj.isCMATempVio);
        MessageObj.message_data_list.append(StatusObj.isCMAVolVio);
        MessageObj.message_data_list.append(StatusObj.isCellVolVio);

    def judgeGPIOInfo(self, StatusObj):
        GPIOInfoList = [];
        if (StatusObj.isCMATempVio == True):
            GPIOInfoList.append({"device": "Pump", "pin_number": 18, "pin_type": GPIO.OUT, "pin_value": GPIO.HIGH});
            print("temperature is too high, the pump continue to work");
        else:
            print("temp is in control, the pump is off")
            GPIOInfoList.append({"device": "Pump", "pin_number": 18, "pin_type": GPIO.OUT, "pin_value": GPIO.LOW});

        if (StatusObj.isCMAVolVio == True or StatusObj.isCellVolVio):
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
        return [StatusObj.isCMAVolVio, StatusObj.isCMATempVio, StatusObj.isCellVolVio]

    def storeToLocalRepo(self, FileObj, MessageObj):
        FileObj.WritetoCVS(MessageObj.message_data_list, MessageObj.final_label_list);
        pass

    def getSendContent(self, dataList, statusList, labelsList):
        dictContent = {"datas": dataList, "status": statusList,
                       "labels": labelsList}
        return dictContent;
    # def getSendContent(self, MessageObj, StatusObj):
    #
    #     dictContent= {"datas": MessageObj.message_data_list , "status": self.getStatusList(StatusObj), "labels": MessageObj.final_label_list}
    #     return dictContent

    def LoopIfNotMeetReq(self, handler, times, *args, **kwargs):

        for i in range(times):
            time.sleep(1);
            if (handler(*args)):
                return True;
        raise Exception(handler.__name__ + " cannot work even after " + str(times) + " times");
        return False;