#!/usr/bin/python3
import time
import os
import csv

class File(object):
	"""docstring for File"""
	def __init__(self, arg):
		super(File, self).__init__()
		self.path = os.getcwd();
        self.Repo = time.strftime('Battery-System %m-%Y') # current: Battery-System %m-%Y
        if(not os.path.isdir(self.path + "/" + "Battery-System-database")):
            os.mkdir(self.path + "/" + "Battery-System-database")
        self.floder = self.path + "/" + "Battery-System-database" + "/" + self.Repo
        if (not os.path.isdir(self.floder)):
            os.mkdir(self.floder)
        self.file ="log" + time.strftime('-Battery-System %d-%m-%Y') + "-" + time.strftime('%H-%M-%S')+".csv"
        self.day = time.strftime('%d') 

    def WritetoCVS(self, list_vol_temp, summary_head):
            # 2.1 update the floder, current, day, file, 
        current_month=time.strftime('Battery-System %m-%Y')
        current_day = time.strftime('%d')
        if(current_month != self.Repo):
            self.Repo = current_month
            self.floder = self.path + "/" + "Battery-System-database" + "/" + self.Repo
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
		