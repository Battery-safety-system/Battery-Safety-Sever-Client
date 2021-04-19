#!/usr/bin/python3
import time
import os
import csv

# !/usr/bin/python3
import time
import os
import csv


class File(object):
    """docstring for File"""

    def __init__(self, labels):

        # print("Initialize File Object")
        self.labels = labels
        self.updateWholeFileSystemVar()
        self.createWholeFilesWithFloders()
        # print("File Object Intialization End")

    def WritetoCVS(self, list_vol_temp, summary_head):
        assert isinstance(list_vol_temp, list);
        assert isinstance(summary_head, list);

        if (self.labels != summary_head):
            self.labels = summary_head
            self.updateWholeFileSystemVar();
            self.createWholeFilesWithFloders();
        elif (time.strftime('%d') != self.day):
            self.updateWholeFileSystemVar();
            self.createWholeFilesWithFloders();
        self.writeList(list_vol_temp);


    def createFloderIfNull(self, path):
        if (not os.path.isdir(path)):
            os.mkdir(path)



    def writeList(self, list):
        with open(self.floder + '/' + self.file, 'a', newline='') as csvfile:
            writer1 = csv.writer(csvfile);
            writer1.writerow(list);

    def updateWholeFileSystemVar(self):
        # print("updateWholeFileSystem() Begin")
        self.path = os.getcwd();
        self.dataBasePath = self.path + "/" + "Battery-System-database"
        self.Repo = time.strftime('Battery-System %m-%Y')
        self.floder = self.path + "/" + "Battery-System-database" + "/" + self.Repo
        self.file = "log" + time.strftime('-Battery-System %d-%m-%Y') + "-" + time.strftime('%H-%M-%S') + ".csv"
        self.day = time.strftime('%d')
        # print("updateWholeFileSystem() End")

    def createWholeFilesWithFloders(self):
        self.createFloderIfNull(self.dataBasePath);
        self.createFloderIfNull(self.floder)
        self.createFileIfNull(self.labels)

    def createFileIfNull(self, labels):
        if (not os.path.isfile(self.floder + '/' + self.file)):
            with open(self.floder + '/' + self.file, 'w', newline='') as csvfile:
                writer1 = csv.writer(csvfile);
                writer1.writerow(labels);

