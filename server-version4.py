#!/usr/bin/python3
import time
import os
import csv
import pickle
import socket
import logging

class Server_PC:
    def __init__(self):
        ## section1: file and floder creation
        self.fileInit();
        self.socketInit();
        self.serverSetting();
        self.error  = 0;
        self.logInit();
    def run(self):
        # while True:
        #     try:
        #         self.socketConnection();
        #         self.labelReceiving();
        #         break;
        #     except Exception as e:
        #         print(e)
        #         print('connection error, reconnect.....')
        #         continue;
        self.socketConnection();
        self.labelReceiving();
        while True:
            try:
                print('start the loop')
                if(self.error == 0):
                    self.messageReceiving();
                    self.statusReceiving();
                    self.printStatus();
                else:
                    print('there is socket error')
                    logging.error('Socket Error')
                    self.socketConnection();
                    self.labelReceiving();
                    self.fileInit();
                    self.error = 0;
            except Exception as e:
                print(e);
                logging.error(e);
                self.error = 1;
        print('end the loop \n')

    def logInit(self):

        logging.basicConfig(level=logging.DEBUG,  # 控制台打印的日志级别
                            filename='ErrorRecord.log',
                            filemode='a',  ##模式，有w和a，w就是写模式，每次都会重新写日志，覆盖之前的日志
                            # a是追加模式，默认如果不写的话，就是追加模式
                            format=
                            '%(asctime)s - %(pathname)s[line:%(lineno)d] - %(levelname)s: %(message)s'
                            # 日志格式
                            )
        logging.info("Start Server")

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
    def serverSetting(self):
        # socket.setdefaulttimeout(5)
        self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server.bind((self.ip_addr, self.ip_port))
        self.server.listen(5)
        print(u'waiting for connect...')

    def socketConnection(self):
        self.connect, (host, port) = self.server.accept()
        print(u'the client %s:%s has connected.' % (host, port))
    # def socketDisConnection(self):


    def socketInit(self):
        self.ip_addr='192.168.137.1'
        self.ip_port = 6699

    def labelReceiving(self):
        self.connect.settimeout(15.0)
        Pre_word = self.connect.recv(3072);
        print("check the label_list Preword");
        assert Pre_word == b'label_list';
        print(Pre_word, 'is correct');
        self.connect.sendall(b'your Pre_word has received.');
        print('receive the label list Preword');
        self.connect.settimeout(None)


        try:
            self.connect.settimeout(15.0)
            self.label_list = pickle.loads(self.connect.recv(9216));
        except Exception as e:
            print(e)
            if(e != 'timed out'):
                self.label_list = pickle.loads(self.connect.recv(9216));
            else:
                self.connect.settimeout(None);
                raise timeout;
        print("label_list has received");
        self.connect.sendall(b'your label_list has received.');
        print(self.label_list);
        self.connect.settimeout(None)

    def messageReceiving(self):
        self.connect.settimeout(15.0)
        Pre_word = self.connect.recv(3072);
        assert Pre_word.decode() == "message_data_list"
        cvs_list = pickle.loads(self.connect.recv(3072));
        self.WritetoCVS(cvs_list, self.label_list);
        self.connect.sendall(b'your cvs_list has received.');
        print('cvs_list is ', cvs_list);
        self.connect.settimeout(None)

    def statusReceiving(self):
        # section 6 get the status
        self.connect.settimeout(15.0)
        print('start status Receiving')
        print('status Preword Receiving')
        Pre_word = self.connect.recv(3072);
        assert Pre_word.decode() == "battery_status"
        print('status Receiving')
        self.battery_status = pickle.loads(self.connect.recv(3072));
        self.connect.sendall(b'your battery_status has received.');
        self.connect.settimeout(None)
    def printStatus(self):
        str1="status: Pump is "
        if(self.battery_status[0] == True):
            str1 += "on"
        else:
            str1 += "off"
        str1 += " Relay is "
        if(self.battery_status[1] == True):
            str1 += "off"
        else :
            str1 += "on"
        print(str1)

server_PC = Server_PC();
server_PC.run();
                    
                

