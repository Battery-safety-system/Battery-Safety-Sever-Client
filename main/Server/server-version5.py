#!/usr/bin/python3
import sys
sys.path.append("C:\\Users\\SERF1\\Desktop\\Battery-Safety-Sever-Client")
from main.Tools.File import File
from main.Tools.ServerDataHandler import DataHandler
from main.Tools.ServerConnection import Connection


class Server_PC:
    def __init__(self):
        ## section1: file and floder creation
        print("check the connection")
        self.ConnectionObj = Connection();
        content = self.ConnectionObj.receiveContent()
        print("initialize the File")
        self.FileObj = File(content["labels"])

        self.DataHandlerObj = DataHandler();

    def run(self):
        datas = [];
        status = [];
        labels = []
        while True:
            print('start the loop')
            try:
                content = self.ConnectionObj.receiveContent()
                datas = content["datas"]
                status = content["status"]
                labels = content["labels"]
            except Exception as e:
                print(e)
                self.ConnectionObj.reconnect()
                self.FileObj.createWholeFileSystemVar()
                self.FileObj.createWholeFilesWithFloders()
                continue

            print(self.DataHandlerObj.getDeviceInfoString(status))
            print(self.DataHandlerObj.getStatusInfoString(status))
            self.FileObj.WritetoCVS(datas, labels)
            print('end the loop \n')


server_PC = Server_PC();
server_PC.run();




                    
                

