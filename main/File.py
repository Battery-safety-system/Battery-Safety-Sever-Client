#!/usr/bin/python3
import time
import os
import csv

class File(object):
	"""docstring for File"""
	def __init__(self):
		super(File, self).__init__()
		self.path = os.getcwd();
        self.Repo = time.strftime('Battery-System %m-%Y') # current: Battery-System %m-%Y
        self.createFloderIfNull(self.path + "/" + "Battery-System-database");
        self.floder = self.path + "/" + "Battery-System-database" + "/" + self.Repo
        self.createFloderIfNull(self.floder);
        self.file ="log" + time.strftime('-Battery-System %d-%m-%Y') + "-" + time.strftime('%H-%M-%S')+".csv"
        self.day = time.strftime('%d') 

    def WritetoCVS(self, list_vol_temp, summary_head):
            # 2.1 update the floder, current, day, file, 
        
        
        self.updateRepoPlusFloder();
        self.updateFilePlusDate();
        self.writeList(summary_head);
        self.writeList(list_vol_temp);


    def createFloderIfNull(self, path):
        if(not os.path.isdir(path)):
            os.mkdir(path)
        pass 

    def updateRepoPlusFloder(self):
        current_month=time.strftime('Battery-System %m-%Y');
        if(current_month != self.Repo):
            self.Repo = current_month
            self.floder = self.path + "/" + "Battery-System-database" + "/" + self.Repo
            os.mkdir(self.floder)

    def updateFilePlusDate(self):
        current_day = time.strftime('%d')
        if(current_day != self.day):
            self.day = current_day
            self.file = "log" + time.strftime('-Battery-System %d-%m-%Y') + "-"+ time.strftime('%H-%M-%S')+".csv";
        pass

	def writeList(self, list):
        if(not os.path.isfile(self.floder + '/' + self.file)):
            with open(self.floder + '/' + self.file, 'w', newline='') as csvfile:
                writer1=csv.writer(csvfile);
                writer1.writerow(list);