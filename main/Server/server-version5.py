#!/usr/bin/python3
import sys
sys.path.append("C:\\Users\\SERF1\\Desktop\\Battery-Safety-Sever-Client")
from main.Tools.File import File
from main.Tools.ServerConnection import Connection
import time

class Server_PC:
    def __init__(self):
        ## section1: file and floder creation
        print("check the connection")
        self.ConnectionObj = Connection();
        print("*****************************************")
        while True:
            try:
                content = self.ConnectionObj.receiveContent()
                break;
            except Exception as e:
                print(e)
                content = self.ConnectionObj.receiveContent()
        self.getLabelsDatasFromContent(content);
        print("*****************************************")


        print("initialize the File")
        self.FileObj = File(self.labels)



    def run(self):

        while True:
            print('start the loop')
            print("current time is " + time.strftime('%H-%M-%S'))
            try:
                content = self.ConnectionObj.receiveContent()
                self.getLabelsDatasFromContent(content);

            except Exception as e:
                print(e)
                self.ConnectionObj.reconnect()
                self.FileObj.createWholeFileSystemVar()
                self.FileObj.createWholeFilesWithFloders()
                continue
            print("warning status: " + str(content["warning"]))
            print("dangerous status: " + str(content["dangerous"]))
            for key in content:
                assert isinstance(key, str)
                if "is" in key and not content[key]:
                    print(key + ": " + content[key])
            self.FileObj.WritetoCVS(self.datas, self.labels)
            print('complete the loop \n')

    def getLabelsDatasFromContent(self, content):
        self.labels = []
        self.datas = [];
        for key in content:
            self.labels.append(key)
            self.datas.append(content[key])

server_PC = Server_PC();
server_PC.run();




                    
                

