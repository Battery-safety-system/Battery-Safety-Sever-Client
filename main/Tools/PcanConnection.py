import cantools
import can
import sys
sys.path.append("/home/pi/Desktop/Battery-Safety-Sever-Client")
import json
from main.Tools.Status import Status
class PcanConnection(object):
    """docstring for PcanConnection"""
    def __init__(self):
        with open('../Client/config.properties') as f:
            data = json.load(f)
            data = data["PcanConnection"]
            for key in data:
                setattr(self, key, data[key]);

        self.bus = can.interface.Bus(channel= self.channel, bustype= self.bustype)


        self.message_dbc = self.getMessageDBC();
        self.reverse_message_dbc =  {v: k for k, v in self.message_dbc.items()}

        self.db = cantools.database.load_file('../Client/Goodwood_15BMUs_IFSpecV3_Node.dbc');

        self.setSyncMessage(); ##
        self.setReqMessage(); # self.Req_message

        # self.Req_message_list = [];

        ## need to get from PCAN
        # self.label_list = []
        # self.final_label_list = []
        # self.battery_list = [];
        #
        # self.message_dict = {};
        # self.message_data_dict = {};
        # self.message_data_list = [];
        self.init();


#         # status
# #         self.CMA_Voltage_High_Dangerous = 42.9 # test
#         self.CMA_Voltage_High_Dangerous = 48.5
#         self.CMA_Voltage_Low_Dangerous = 33
# #         self.CMA_Voltage_Low_Dangerous = 42.5 # test
#
#         self.CMA_Voltage_High_Warning = 47.5
# #         self.CMA_Voltage_High_Warning = 43.9 #test
#         self.CMA_Voltage_Low_Warning = 34
# #         self.CMA_Voltage_Low_Warning = 42.5 # test
#
# #         self.CMA_Temp_Dangerous = 23 # test
#         self.CMA_Temp_Dangerous = 50
#         self.CMA_Temp_Warning = 40;
# #         self.CMA_Temp_Warning = 23; # test
#         self.CMA_Temp_security = 30
#         #self.CMA_Temp_security = 18 # test
#
#         self.Cell_Voltage_High_Warning = 4.1
# #         self.Cell_Voltage_High_Warning = 3.56 # test
#         self.Cell_Voltage_Low_Warning = 2.8
# #         self.Cell_Voltage_Low_Warning = 3.61 # test
#         self.Cell_Voltage_High_Dangerous = 4.2
# #         self.Cell_Voltage_High_Dangerous = 3.56 #3 test
# #         self.Cell_Voltage_Low_Dangerous = 2.7
#         self.Cell_Voltage_Low_Dangerous = 3.62 # test
#
#         self.cellVoltageNum = 12

    def init(self):
        # 1.1 get the battery number
        self.getBatteryListFromPcan();
        self.getReqMessageList();
        self.getLabelListPlusMessageDictFromPcan()
        if(not self.checkIfPcanLabelsReadingRight()):
            raise Exception("Error!!!! Pcan Init has Problem, pcan Reading is Wrong")
        # print(f'label list: {self.label_list}')
        # 1.4 construct the label list
        self.getFinalLabelList();
        pass

    def getMessageDBC(self):
        message_dbc = {};
        for i in range(1, 5):
            for j in range(1, 16):
                key_id = str(i) + '8' + str(hex(j))[2:];
                value_str = 'BMU' + str(j).zfill(2) + '_pdo' + str(i);
                message_dbc[int(key_id, 16)] = value_str;
        for i in range(5, 9):
            for j in range(1, 16):
                key_id = str(i - 4) + '9' + str(hex(j))[2:];
                value_str = 'BMU' + str(j).zfill(2) + '_pdo' + str(i);
                message_dbc[int(key_id, 16)] = value_str;
        return message_dbc;

    def setReqMessage(self):
        for battery_id in range(1, 16):
            Req_Name = 'BMU' + str(battery_id).zfill(2) + '_SDO_Req';
            BMU_Req_Data = b'\x2F\x05\x18\x01\x00\x00\x00\x00';
            Req_message = 'BMU' + str(battery_id).zfill(2) + '_Req_send_message';
            message_content = self.db.get_message_by_name(Req_Name)
            setattr(self, Req_message,
                    can.Message(arbitration_id=message_content.frame_id, data=BMU_Req_Data, extended_id=False));

    def setSyncMessage(self):
        sync = self.db.get_message_by_name('SYNC');
        sync_data = sync.encode({'Sync_Count': 0xFF});
        self.sync_message = can.Message(arbitration_id=0x80, data=sync_data, extended_id=False)


# ----------------------------- Main Function --------------------------------
    def getLabels(self):
        return self.final_label_list;

    def getDatas(self):
        return self.message_data_list;

    def close(self):
        self.bus.shutdown();



# -------------------------- sending function ----------------------------------------
    def sendMessage(self, message):
        # print("Send Message: " + str(message.arbitration_id))
        self.bus.send(message);
        # print("sendMessage() end");

    def sendMessageList(self, messageList):
        # print("send Message list id: " + str([message.arbitration_id for message in messageList]))
        for Req_message in messageList:
            self.bus.send(Req_message);
        # print("sendMessageList() end");

# ------------------------ get Info from Pcan function --------------------------------------

    def getBatteryListFromPcan(self):
#         print("Begin getBatteryListFromPcan()")
        self.sendMessage(self.sync_message);
        count = 0;
        label_list = [];
        while True:
            message = self.bus.recv();
#             print(message.arbitration_id)
            if(message.arbitration_id not in self.message_dbc):
                count += 1;
            else:
                message_name = self.message_dbc[message.arbitration_id];
                label_list.append(message_name);
                count = 0;
            if(count > self.exitNum):
                break;
        # label shoud be sorted [BMU01_pdo01, BMU02_pdo02 ...]
        if(len(label_list) == 0):
#             print("label_list is " + str(label_list))
            self.getBatteryListFromPcan()
            return;
#             raise Exception("PcannConnection Error!!!! label list length is 0")
        label_list.sort();
        battery_list = list(set([int(elem[3:5]) for elem in label_list]));
        self.battery_list = battery_list;
        # print("battery_list: " + str(battery_list))
        # print("getBatteryListFromPcan() end");
        
    def getLabelListPlusMessageDictFromPcan(self):
        # print("Begin getLabelListPlusMessageDictFromPcan()")
                # 1.3 get the total pdo number with Req sending
        self.sendMessage(self.sync_message);
        self.sendMessageList(self.Req_message_list);
        count = 0;
        label_list = [];
        message_dict = {}
        while True:
            message = self.bus.recv();
            if(message.arbitration_id not in self.message_dbc):
                count += 1;
            else:
                message_name = self.message_dbc[message.arbitration_id];
                message_dict[message_name] = message;
                label_list.append(message_name);
                count = 0;
            if(count > self.exitNum):
                break;

        if (len(label_list) < 10):
            raise Exception("Error!!! PcanConnection: getLabelListPlusMessageDictFromPcan: Pcan label_list reading error, check Pcan Connection please")
            # self.getLabelListPlusMessageDictFromPcan();
            # return ;

        label_list.sort(); #[BMU01_pdo01, BMU02_pdo02 ...]
        self.label_list = label_list;
        self.message_dict = message_dict;
        # print("getLabelListPlusMessageDictFromPcan() end");

    def getFinalLabelList(self):
        # print("Begin getFinalLabelList()")
        final_label_list = [] # BMU01_Max_temp, BMU01_Min_temp
        for label in self.label_list:
            A_message = self.message_dict[label];
            battery_name = label[0:5] #BMU01 or BMU02
            data_decode = self.db.decode_message(A_message.arbitration_id, A_message.data);
            for key, value in data_decode.items(): # key: Max_temp
                final_label = battery_name + '_' + key;
                final_label_list.append(final_label);
        final_label_list.sort();
        self.final_label_list = final_label_list;
        # print("final_label_list: " + str(final_label_list))
        # print("getFinalLabelList() end");

    def getDataFromPcan(self):
        # print("Begin getDataFromPcan()")
        self.sendMessage(self.sync_message);
        self.sendMessageList(self.Req_message_list)
        message_dict = {};
        count = 0;
        while True:
            message = self.bus.recv();
            if(message.arbitration_id not in self.message_dbc ):
                count += 1;
                if(count > self.exitNum ):
                    break;
                continue;
            message_name = self.message_dbc[message.arbitration_id]
            message_dict[message_name] = message;
            count = 0;
        self.message_dict = message_dict;
        self.handleData();
        # print("getDataFromPcan() end");
        return self.message_data_list;

    def getReqMessageList(self):
        # print("Begin getReqMessageList()")
        Req_message_list = [];
        Req_list = ['self.' + 'BMU' + str(battery_id).zfill(2) + '_Req_send_message' for battery_id in
                    self.battery_list];
        for ele in Req_list:
#             print(ele)
            Req_message_list.append(eval(ele));
        self.Req_message_list = Req_message_list;
        # print("ReqMessage List id: ")
        # print([ Req_message.arbitration_id  for Req_message in self.Req_message_list]);
        # print("ReqMessage List: " + str(self.Req_message_list))
        # print("getReqMessageList() end");


    def getAllInfo(self):
        # print("Begin getAllInfo()")
        # 1.1 get the battery number
        self.getBatteryListFromPcan();
        self.getReqMessageList();
        self.getLabelListPlusMessageDictFromPcan()
        # print(f'label list: {self.label_list}')
        # 1.4 construct the label list
        self.getFinalLabelList(); # update the final labels
        self.getDataFromPcan()

        # print("getAllInfos() end");

    def handleData(self):
        # print("Begin handleData()");
        message_data_dict = {}  # {BMU01_MAXTemp: xxx, BMU01_MinTemp: xxx, ...}
        message_data_list = [];  # date, time, BMU01_MAXTemp, BMU01_MinTemp, ... (based on the label)
        for label in self.label_list:  # BMU01_pdo1, BMU01_pdo2
            A_message = self.message_dict[label];
            battery_name = label[0:5]  # BMU01 or BMU02
            data_decode = self.db.decode_message(A_message.arbitration_id, A_message.data);
            for key, value in data_decode.items():  # key: Max_temp
                final_label = battery_name + '_' + key;
                message_data_dict[final_label] = value;
        for label in self.final_label_list:
            assert label in message_data_dict;
            value = message_data_dict[label];
            message_data_list.append(value);

        self.message_data_dict = message_data_dict;
        self.message_data_list = message_data_list;
        # print("handleData() end")

# ------------------------- Status Function --------------------------------------

    def updateStatusWithCMAVoltage(self, status):
        assert isinstance(status, Status)
        max_CMA_Voltage = -1;
        min_CMA_Voltage = 1000;
        for battery in self.battery_list:
            battery_str = 'BMU' + str(battery).zfill(2)
            label = battery_str + '_' + 'CMA_Voltage';
            CMA_Voltage = self.message_data_dict[label];
            if(max_CMA_Voltage < CMA_Voltage):
                max_CMA_Voltage = CMA_Voltage
            if(min_CMA_Voltage > CMA_Voltage):
                min_CMA_Voltage = CMA_Voltage
        # print("max_CMA_Voltage: " + str(max_CMA_Voltage))
        # print("min_CMA_Voltage: " + str(min_CMA_Voltage))
        if max_CMA_Voltage >= self.CMA_Voltage_High_Dangerous:
            status.dangerous = True;
            status.isPcanVoltageHighDangerous = True;
            print("Cma voltage high dangeroius")
        if max_CMA_Voltage >= self.CMA_Voltage_High_Warning:
            status.warning = True;
            status.isPcanVoltageHighWarning = True;
            print("CMA_Voltage_high warning")
        if min_CMA_Voltage <= self.CMA_Voltage_Low_Dangerous:
            status.dangerous = True;
            status.isPcanVoltageLowDangerous = True;
            print("CMA_Voltage_low dangerous")
            
        if min_CMA_Voltage <= self.CMA_Voltage_Low_Warning:
            status.warning = True;
            print("CMA_Voltage_low warning")
            status.isPcanVoltageLowWarning = True

    

    def updateStatusWithTemp(self, status):
        assert isinstance(status, Status)
        max_temp = -1; 
        for battery in self.battery_list:
            battery_str = 'BMU' + str(battery).zfill(2)
            label = battery_str + '_' + 'CMA_Max_Temp';
            CMA_Max_Temp = self.message_data_dict[label];
            if max_temp < CMA_Max_Temp:
                max_temp = CMA_Max_Temp
             
            if CMA_Max_Temp >= self.CMA_Temp_Dangerous:  ##40?
                status.dangerous = True;
                status.isPcanTempDangerous = True;
                print("CMA_Max_Temp dangerous: " + str(CMA_Max_Temp))
                if battery not in status.temperature_voliated_battery:
                    status.temperature_voliated_battery.append(battery);
                
            if CMA_Max_Temp >= self.CMA_Temp_Warning:
                print("CMA_Max_Temp warning: " + str(CMA_Max_Temp))
                status.warning = True;
                status.isPcanTempWarning = True;
                if battery not in status.temperature_voliated_battery:
                    status.temperature_voliated_battery.append(battery);
                pass
        # print("Max temp: " + str(max_temp))
        # print("temperature voliated battery: " + str(status.temperature_voliated_battery))
        for battery in status.temperature_voliated_battery:
            battery_str = 'BMU' + str(battery).zfill(2)
            label = battery_str + '_' + 'CMA_Max_Temp';
            CMA_Max_Temp = self.message_data_dict[label];
            if CMA_Max_Temp <= self.CMA_Temp_security:  ##40?
                status.temperature_voliated_battery.remove(battery);



    def updateStatusWithCellVoltage(self, status):
        assert isinstance(status, Status)
        Max_Cell_Voltage = -1;
        Min_Cell_Voltage = 1000;
        for battery in self.battery_list:
            battery_str = 'BMU' + str(battery).zfill(2);
            for i in range(1, self.cellVoltageNum):
                label = battery_str + '_' + 'Cell' + '_' + str(i) + '_Voltage'
                if(self.message_data_dict[label] > Max_Cell_Voltage) :
                    Max_Cell_Voltage = self.message_data_dict[label]
                if(self.message_data_dict[label] < Min_Cell_Voltage ):
                    Min_Cell_Voltage = self.message_data_dict[label];
#         print("Max_Cell_Voltage: " + str(Max_Cell_Voltage));
#         print("Min_Cell_voltage: " + str(Min_Cell_Voltage))
        if Max_Cell_Voltage >= self.Cell_Voltage_High_Dangerous:
            print("max cell voltage high dangerous : " + str(Max_Cell_Voltage))
            status.isPcanVoltageHighDangerous = True;
            status.dangerous = True;
        if Max_Cell_Voltage >= self.Cell_Voltage_High_Warning:
            print("max cell voltage high warning : " + str(Max_Cell_Voltage))
            status.isPcanVoltageHighWarning = True;
            status.warning = True;
        if Min_Cell_Voltage <= self.Cell_Voltage_Low_Dangerous:
            print("min cell voltage low dangerous : " + str(Min_Cell_Voltage))
            status.isPcanVoltageHighWarning = True;
            status.dangerous = True;
        if Min_Cell_Voltage <= self.Cell_Voltage_Low_Warning:
            print("cell voltage low warning: " + str(Min_Cell_Voltage))
            status.isPcanVoltageLowWarning = True;
            status.warning = True;
        

    def updateStatus(self, status):
        # print("Begin to detect the status")
        self.updateStatusWithCMAVoltage(status);
        self.updateStatusWithTemp(status);
        self.updateStatusWithCellVoltage(status);
        # print(self.message_data_dict)
        # print("detectStatus End")


    def checkIfPcanLabelsReadingRight(self):
        if(self.label_list == 0):
            return False;
        else:
            return True;