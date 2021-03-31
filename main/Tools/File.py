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

        print("Initialize File Object")
        self.labels = labels
        self.createWholeFileSystemVar()
        self.createWholeFilesWithFloders()
        print("File Object Intialization End")

    def WritetoCVS(self, list_vol_temp, summary_head):

        print("Begin WritetoCVS")
        self.updateFileByLabels(summary_head)
        self.updateFilesWithFlodersByDates();
        self.writeList(list_vol_temp);
        print("WritetoCVS End")

    def updateFileByLabels(self, summary_head):
        if(self.labels != summary_head):
            for i in range(len(self.labels)):
                if (self.labels[i] != summary_head[i]):
                    print("labels: " + self.labels[i])
                    print("summary_head: " + summary_head[i])
            print("labels and summary_head are different")
            print("labels: " + str(self.labels))
            print("summary_head: " + str(summary_head))
            self.labels = summary_head
            self.createWholeFileSystemVar();
            self.createWholeFilesWithFloders();

    def createFloderIfNull(self, path):
        if (not os.path.isdir(path)):
            os.mkdir(path)


    def updateFilesWithFlodersByDates(self):
        current_day = time.strftime('%d')
        if (current_day != self.day):
            self.createWholeFileSystemVar();
            self.createWholeFilesWithFloders();

    def writeList(self, list):
        with open(self.floder + '/' + self.file, 'a', newline='') as csvfile:
            writer1 = csv.writer(csvfile);
            writer1.writerow(list);

    def createWholeFileSystemVar(self):
        print("updateWholeFileSystem() Begin")
        self.path = os.getcwd();
        self.dataBasePath = self.path + "/" + "Battery-System-database"
        self.Repo = time.strftime('Battery-System %m-%Y')
        self.floder = self.path + "/" + "Battery-System-database" + "/" + self.Repo
        self.file = "log" + time.strftime('-Battery-System %d-%m-%Y') + "-" + time.strftime('%H-%M-%S') + ".csv"
        self.day = time.strftime('%d')
        print("updateWholeFileSystem() End")

    def createWholeFilesWithFloders(self):
        self.createFloderIfNull(self.dataBasePath);
        self.createFloderIfNull(self.floder)
        self.createFileIfNull(self.labels)

    def createFileIfNull(self, labels):
        if (not os.path.isfile(self.floder + '/' + self.file)):
            with open(self.floder + '/' + self.file, 'w', newline='') as csvfile:
                writer1 = csv.writer(csvfile);
                writer1.writerow(labels);

