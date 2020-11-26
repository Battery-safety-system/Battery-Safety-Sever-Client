#!/usr/bin/python3
import time
import can
import RPi.GPIO as GPIO
import cantools
import os
import csv
import socket
import pickle

class Battery_System:
    def __init__(self):
        # GPIOSetting
        self.GPIOSetting(Pump = 18, Relay = 16);
        self.SyncMessageSetting();
        self.ReqMessageSetting();
        self.socketConnection();
        self.dbcCreationg();
        self.error = 0;
        self.fileInit();
    def run(self):
            self.getLabel();
            self.sendLabel();
            while True:
                try:
                    self.getData();
                    self.handleData();
                    self.detectStatus();
                except:
                    continue;
                
                try:
                    if(self.error == 0):
                        self.sendData();
                        self.sendStatus();
                    else:
                        self.socketConnection();
                        self.sendLabel();
                        self.sendData();
                        self.sendStatus();
                        self.error = 0; 
                except Exception as e:
                    self.error = 1; 
                    print(e)
                self.activateDevice();
                pass

    def fileInit(self):
        self.path = os.getcwd();
        self.current = time.strftime('Battery-System %m-%Y') # current: Battery-System %m-%Y
        if(not os.path.isdir(self.path + "/" + "Battery-System-database")):
            os.mkdir(self.path + "/" + "Battery-System-database")
        self.floder = self.path + "/" + "Battery-System-database" + "/" + self.current
        if (not os.path.isdir(self.floder)):
            os.mkdir(self.floder)
        self.file ="log" + time.strftime('-Battery-System %d-%m-%Y') + "-" + time.strftime('%H-%M-%S')+".csv"
        self.day = time.strftime('%d')

        ## section2: WritetoCVS function
    def WritetoCVS(self, list_vol_temp, summary_head):
            # 2.1 update the floder, current, day, file, 
        current_month=time.strftime('Battery-System %m-%Y')
        current_day = time.strftime('%d')
        if(current_month != self.current):
            self.current = current_month
            self.floder = self.path + "/" + "Battery-System-database" + "/" + self.current
            os.mkdir(self.floder)
        if(current_day != self.day):
            self.day = current_day
            self.file = "log" + time.strftime('-Battery-System %d-%m-%Y') + "-"+ time.strftime('%H-%M-%S')+".csv";

        # 2.2 make the header if the file is new
        if(not os.path.isfile(self.floder + '/' + self.file)):
            with open(self.floder + '/' + self.file, 'w', newline='') as csvfile:
                writer1=csv.writer(csvfile);
                writer1.writerow(summary_head);
        # 2.3 insert the data
        with open(self.floder + '/' + self.file, 'a', newline='') as csvfile:
            writer1=csv.writer(csvfile)
            writer1.writerow(list_vol_temp)


    def GPIOSetting(self, Pump = 18, Relay = 16):
        self.Pump = Pump; self.Relay = Relay;
        GPIO.setwarnings(False)
        GPIO.setmode(GPIO.BCM)
        GPIO.setup(Pump, GPIO.OUT)
        GPIO.setup(Relay, GPIO.OUT)
        GPIO.output(Relay, GPIO.HIGH);
        GPIO.output(Pump, GPIO.LOW);

    def SyncMessageSetting(self):
        ## bus set up
        bustype = 'socketcan'
        channel = 'can0'
        self.bus = can.interface.Bus(channel=channel, bustype=bustype)

        ### sync message setting
        self.db=cantools.database.load_file('Goodwood_15BMUs_IFSpecV3_Node.dbc');
        sync_message=self.db.get_message_by_name('SYNC');
        sync_data=sync_message.encode({'Sync_Count':0xFF});
        self.send_message = can.Message(arbitration_id = 0x80, data = sync_data, extended_id = False)
    def ReqMessageSetting(self):
        for battery_id in range(1, 16):
            Req_Name = 'BMU' + str(battery_id).zfill(2)+'_SDO_Req';
            BMU_Req_Data = b'\x2F\x05\x18\x01\x00\x00\x00\x00';
            #BMU14_Req_send_message = can.Message(arbitration_id=0x60e, data=BMU14_Req_data, extended_id=False)
            Req_message = 'BMU' + str(battery_id).zfill(2)+'_Req_send_message';
            message_content = self.db.get_message_by_name(Req_Name)
            #print(can.Message(arbitration_id= message_content.frame_id, data=BMU_Req_Data, extended_id=False))
            setattr(self, Req_message, can.Message(arbitration_id= message_content.frame_id, data=BMU_Req_Data, extended_id=False));
    def dbcCreationg(self):
        self.message_dbc = {};
        for i in range(1, 5):
            for j in range(1, 16):
                key_id = str(i) + '8' + str(hex(j))[2:];
                value_str = 'BMU' + str(j).zfill(2)+'_pdo' + str(i);
                self.message_dbc[int(key_id, 16)] = value_str;
        for i in range(5, 9):
            for j in range(1, 16):
                key_id = str(i - 4) + '9' + str(hex(j))[2:];
                value_str = 'BMU' + str(j).zfill(2)+'_pdo' + str(i);
                self.message_dbc[int(key_id, 16)] = value_str;
        self.invert_message_dbc =  {v: k for k, v in self.message_dbc.items()}
        self.temperature_voliated_battery = [];
        
    def socketConnection(self):
        #### ip address
        ip_addre='192.168.137.1'
        ip_port = 6699
        self.client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.client.settimeout(15)
        self.client.connect((ip_addre, ip_port))
        self.client.settimeout(None);
        print('socket has connected')

    def initSocket(self):
        self.client.settimeout(None);

    def sendSynMessage(self):
        self.bus.send(self.send_message);

    def sendReqMessage(self, Req_message_list):
        for Req_message in Req_message_list:
            print(Req_message)
            self.bus.send(Req_message);
        pass
    def getLabel(self):
        # 1.1 get the battery number
        self.sendSynMessage();
        count = 0;
        label_list = [];
        while True:
            message = self.bus.recv();
            if(message.arbitration_id not in self.message_dbc):
                count += 1;
            else:
                message_name = self.message_dbc[message.arbitration_id];
                label_list.append(message_name);
                count = 0;
            if(count > 10):
                break;
        # label shoud be sorted [BMU01_pdo01, BMU02_pdo02 ...]
        label_list.sort();

        # 1.2 get the req_message
        # example battery_list [1, 3]
        self.battery_list = list(set([int(elem[3:5]) for elem in label_list]));
        # Req_message_list = [BMU01_Req_send_message, BMU03_Req_send_message];
        #print([ eval('self.' + 'BMU'+str(battery_id).zfill(2)+'_Req_send_message') for battery_id in battery_list]);
        # print();
        self.Req_message_list = [];
        Req_list = ['self.' + 'BMU'+str(battery_id).zfill(2)+'_Req_send_message' for battery_id in self.battery_list];
        for ele in Req_list:
            print(ele)
            self.Req_message_list.append(eval(ele));
         
        
        # 1.3 get the total pdo number with Req sending
        self.sendSynMessage();
        self.sendReqMessage(self.Req_message_list);
        count = 0;
        self.label_list = [];
        message_dict = {}
        while True:
            message = self.bus.recv();
            if(message.arbitration_id not in self.message_dbc):
                count += 1;
        
            else:
                message_name = self.message_dbc[message.arbitration_id];
                message_dict[message_name] = message;
                self.label_list.append(message_name);
                count = 0;
            if(count > 10):
                break;
        self.label_list.sort(); #[BMU01_pdo01, BMU02_pdo02 ...]
        print('label list')
        print(self.label_list)

        # 1.4 construct the label list
        self.final_label_list = [] # BMU01_Max_temp, BMU01_Min_temp
        for label in self.label_list:
            A_message = message_dict[label];
            battery_name = label[0:5] #BMU01 or BMU02
            data_decode = self.db.decode_message(A_message.arbitration_id, A_message.data);
            for key, value in data_decode.items(): # key: Max_temp
                final_label = battery_name + '_' + key;
                self.final_label_list.append(final_label);
        self.final_label_list.sort();
        self.final_label_list.insert(0, 'time');
        self.final_label_list.insert(0, 'date'); # final_label_list: [date time BMU01_Max_temp .... BMU02_Max_temp ...]

    def sendLabel(self):
        # 1.5 send the label list
        print('in section sendLabel')
        print('final_label_list is:')
        print(self.final_label_list)
        final_label_list_pickle = pickle.dumps(self.final_label_list);
        self.client.settimeout(15)
        print('send label_list')
        self.client.send(b'label_list')
        rec_data = self.client.recv(1024)
        print(b'form server receive:' + rec_data);
        
        print('send final_label_list_pickle')
        self.client.send(final_label_list_pickle)
        print("final_label_list has sent")
        rec_data = self.client.recv(1024)
        print(b'form server receive:' + rec_data);
        self.client.settimeout(None);


    def getData(self):
        self.bus.send(self.send_message);
        for Req_message in self.Req_message_list:
            self.bus.send(Req_message);
        print("all the message has sent via pcan, start to receive message");
        # 2.2 receive the message 
        self.message_dict = {};
        count = 0;
        while True:
            message = self.bus.recv();
            if(message.arbitration_id not in self.message_dbc ):
                count += 1;
                if(count > 10 and len(self.message_dict) != 0):
                    break;
                continue;
        #data_decode=db.decode_message(message.arbitration_id, message.data)
            message_name = self.message_dbc[message.arbitration_id]
            self.message_dict[message_name] = message;
            count = 0;

        print("all the message has received, start to handle the data");
        
    def handleData(self):
        self.message_data_dict = {} # {BMU01_MAXTemp: xxx, BMU01_MinTemp: xxx, ...}
        self.message_data_list = []; # date, time, BMU01_MAXTemp, BMU01_MinTemp, ... (based on the label)
        for label in self.label_list: # BMU01_pdo1, BMU01_pdo2
            A_message = self.message_dict[label];
            battery_name = label[0:5] #BMU01 or BMU02
            data_decode = self.db.decode_message(A_message.arbitration_id, A_message.data);
            for key, value in data_decode.items(): # key: Max_temp
                final_label = battery_name + '_' + key;
                self.message_data_dict[final_label] = value;
        for label in self.final_label_list:
            if(label == 'date'):
                self.message_data_list.append(time.strftime('%d-%m-%Y'));
            elif(label == 'time'):
                self.message_data_list.append(time.strftime('%H:%M:%S'));
            else:
                assert label in self.message_data_dict;
                value = self.message_data_dict[label];
                self.message_data_list.append(value);
        print("message data has been handle, start to send the message data")

    def sendData(self):
        self.WritetoCVS(self.message_data_list, self.final_label_list);
        self.client.settimeout(15)
        self.client.send("message_data_list".encode())
        self.client.send(pickle.dumps(self.message_data_list))
        print("message_data_list has send")
        rec_data = self.client.recv(1024)
        print(b'form server receive:' + rec_data);
        self.client.settimeout(None);


    def detectStatus(self):
        # 3.1 setting parameter
        self.volLimited = False;
        self.tempHigh = False; 
        # 3.2 detect the data
        # 3.2.1 check the temperature
        for battery in self.battery_list:
            battery_str = 'BMU'+str(battery).zfill(2)
            label = battery_str + '_' + 'CMA_Max_Temp';
            CMA_Max_Temp = self.message_data_dict[label];
            if CMA_Max_Temp >= 35:  ##40?
                self.temperature_voliated_battery.append(battery);
        for battery in self.temperature_voliated_battery:
            battery_str = battery_str + '_' + 'CMA_Max_Temp';
            CMA_Max_Temp = self.message_data_dict[label];
            if CMA_Max_Temp <= 30:  ##40?
                self.temperature_voliated_battery.remove(battery);
            if not self.temperature_voliated_battery:
                self.tempHigh = False;
            else: 
                self.tempHigh = True;
            # 3.2.2 check the voltage
        for battery in self.battery_list:
            battery_str = 'BMU'+str(battery).zfill(2)
            label = battery_str + '_' + 'CMA_Voltage';
            CMA_Voltage = self.message_data_dict[label];
            if CMA_Voltage >= 48 or CMA_Voltage <= 33:
                self.volLimited = True;

    def sendStatus(self):
        # 3.3 send the battery status
        battery_status = [self.tempHigh, self.volLimited];
        self.client.settimeout(15)
        self.client.send("battery_status".encode())
        self.client.send(pickle.dumps(battery_status))
        print("battery_status has send")
        rec_data = self.client.recv(1024)
        print(b'form server receive:' + rec_data);
        self.client.settimeout(None);



    def activateDevice(self):
        # activate the pump and ramp or not
        if(self.tempHigh == True):
            GPIO.output(self.Pump, GPIO.HIGH);
            print("temperature is too high, the pump continue to work");
            time.sleep(4);
            print("Let's start another loop");
            return;
        else:
            print("temp is in control, the pump is off")
            GPIO.output(self.Pump, GPIO.LOW)

        if(self.volLimited == True):
            GPIO.output(self.Relay, GPIO.LOW);
            print("voltage is out of control, break the program")
            exit();
        else:
            print("voltage is in control, the relay is on")
            GPIO.output(self.Relay, GPIO.HIGH);
        time.sleep(4)
        print("one loop is completed, start another loop\n")


Battery1 = Battery_System();
Battery1.run();








