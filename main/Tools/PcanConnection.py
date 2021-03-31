import cantools
import can
import time
from Status import Status
class PcanConnection(object):
    """docstring for PcanConnection"""
    def __init__(self):
        super(PcanConnection, self).__init__()
        self.bustype = 'socketcan'
        self.channel = 'can0'
        self.bus = can.interface.Bus(channel= self.channel, bustype= self.bustype)

        self.message_dbc = self.getMessageDBC();
        self.reverse_message_dbc =  {v: k for k, v in self.message_dbc.items()}

        self.db=cantools.database.load_file('Goodwood_15BMUs_IFSpecV3_Node.dbc');

        self.setSyncMessage(); ##
        self.setReqMessage(); # self.Req_message

        self.Req_message_list = [];

        ## need to get from PCAN
        self.label_list = []
        self.final_label_list = []
        self.battery_list = [];

        self.message_dict = {};
        self.message_data_dict = {};
        self.message_data_list = [];
        self.init();

        # status
        self.CMA_Max_Voltage_Vio = 48
        self.CMA_Min_Voltage_Vio = 33

        self.CMA_Max_Temp_Vio = 40
        self.CMA_Temp_release = 30

        self.Max_Voltage_Vio = 4.1
        self.Min_Voltage_Vio = 2.8
        self.cellVoltageNum = 12


        print("PCAN Connection Initialization end");

    def init(self):
        # 1.1 get the battery number
        self.getBatteryListFromPcan();
        self.getReqMessageList();
        self.getLabelListPlusMessageDictFromPcan()
        print(f'label list: {self.label_list}')
        # 1.4 construct the label list
        self.getFinalLabelList();
        pass
    def getLabels(self):
        return self.final_label_list;

    def getDatas(self):
        return self.message_data_list;

#   communication Information
    def sendMessage(self, message):
        print("Send Message: " + str(message.arbitration_id))
        self.bus.send(message);
        print("sendMessage() end");
        
    def sendMessageList(self, messageList):
        print("send Message list id: " + str([message.arbitration_id for message in messageList]))
        for Req_message in messageList:
            self.bus.send(Req_message);
        print("sendMessageList() end");

    def getBatteryListFromPcan(self):
        print("Begin getBatteryListFromPcan()")
        self.sendMessage(self.sync_message);
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
        battery_list = list(set([int(elem[3:5]) for elem in label_list]));
        self.battery_list = battery_list;
        print("getBatteryListFromPcan() end");
        
    def getLabelListPlusMessageDictFromPcan(self):
        print("Begin getLabelListPlusMessageDictFromPcan()")
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
            if(count > 10):
                break;
        label_list.sort(); #[BMU01_pdo01, BMU02_pdo02 ...]

        self.label_list = label_list;
        self.message_dict = message_dict;
        print("getLabelListPlusMessageDictFromPcan() end");

    def getFinalLabelList(self):
        print("Begin getFinalLabelList()")
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
        print("final_label_list: " + str(final_label_list))
        print("getFinalLabelList() end");

    def getDataFromPcan(self):
        print("Begin getDataFromPcan()")
        self.sendMessage(self.sync_message);
        self.sendMessageList(self.Req_message_list)
        message_dict = {};
        count = 0;
        while True:
            message = self.bus.recv();
            if(message.arbitration_id not in self.message_dbc ):
                count += 1;
                if(count > 10 and len(message_dict) != 0):
                    break;
                continue;
            message_name = self.message_dbc[message.arbitration_id]
            message_dict[message_name] = message;
            count = 0;
        self.message_dict = message_dict;
        self.handleData();
        print("getDataFromPcan() end");
        return self.message_data_list;


    def getAllInfo(self):
        print("Begin getAllInfo()")
        # 1.1 get the battery number
        self.getBatteryListFromPcan();
        self.getReqMessageList();
        self.getLabelListPlusMessageDictFromPcan()
        print(f'label list: {self.label_list}')
        # 1.4 construct the label list
        self.getFinalLabelList(); # update the final labels
        self.getDataFromPcan(); # update the data
        print("getAllInfos() end");


#   message structure

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

    def getReqMessageList(self):
        print("Begin getReqMessageList()")
        Req_message_list = [];
        Req_list = ['self.' + 'BMU' + str(battery_id).zfill(2) + '_Req_send_message' for battery_id in
                    self.battery_list];
        for ele in Req_list:
            print(ele)
            Req_message_list.append(eval(ele));
        self.Req_message_list = Req_message_list;
        print("ReqMessage List id: ")
        print([ Req_message.arbitration_id  for Req_message in self.Req_message_list]);
        print("ReqMessage List: " + str(self.Req_message_list))
        print("getReqMessageList() end");

## Data Handler
    def handleData(self):
        print("Begin handleData()");
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
        print("handleData() end")


    def detectVoltage(self, status):
        assert isinstance(status, Status)
        isvolLimited = False;
        for battery in self.battery_list:
            battery_str = 'BMU' + str(battery).zfill(2)
            label = battery_str + '_' + 'CMA_Voltage';
            CMA_Voltage = self.message_data_dict[label];
            if CMA_Voltage >= self.CMA_Max_Voltage_Vio or CMA_Voltage <= self.CMA_Min_Voltage_Vio:
                isvolLimited = True;
        status.isCMAVolVio = isvolLimited;

    def detectTemp(self, status):
        assert isinstance(status, Status)
        istempHigh = False;
        for battery in self.battery_list:
            battery_str = 'BMU' + str(battery).zfill(2)
            label = battery_str + '_' + 'CMA_Max_Temp';
            CMA_Max_Temp = self.message_data_dict[label];
            if CMA_Max_Temp >= self.CMA_Max_Temp_Vio:  ##40?
                status.temperature_voliated_battery.append(battery);
        for battery in status.temperature_voliated_battery:
            battery_str = 'BMU' + str(battery).zfill(2)
            label = battery_str + '_' + 'CMA_Max_Temp';
            CMA_Max_Temp = self.message_data_dict[label];
            if CMA_Max_Temp <= self.CMA_Temp_release:  ##40?
                status.temperature_voliated_battery.remove(battery);
            if not status.temperature_voliated_battery:
                istempHigh = False;
            else:
                istempHigh = True;
        status.isCMATempVio = istempHigh;

    def detectCellVoltageViolated(self, status):
        assert isinstance(status, Status)
        isCVViolated = False;
        for battery in self.battery_list:
            Max_Cell_Voltage = -1;
            Min_Cell_Voltage = 1000;
            battery_str = 'BMU' + str(battery).zfill(2);
            for i in range(1, self.cellVoltageNum):
                label = battery_str + '_' + 'Cell' + '_' + str(i) + '_Voltage'
                if(self.message_data_dict[label] > Max_Cell_Voltage) :
                    Max_Cell_Voltage = self.message_data_dict[label]
                if(self.message_data_dict[label] < Min_Cell_Voltage ):
                    Min_Cell_Voltage = self.message_data_dict[label];
            print("Max_Cell_Voltage: " + str(Max_Cell_Voltage));
            print("Min_Cell_voltage: " + str(Min_Cell_Voltage))
            if Max_Cell_Voltage >= self.Max_Voltage_Vio or Min_Cell_Voltage < self.Min_Voltage_Vio:  ##40?
                isCVViolated = True;
        print("is Cell Voltage Violated: " + str(isCVViolated))
        status.isCellVolVio = isCVViolated;

    def detectStatus(self, status):
        print("Begin to detect the status")
        self.detectVoltage(status);
        self.detectTemp(status);
        self.detectCellVoltageViolated(status);
        print(self.message_data_dict)
        print(
            "is there any voltage violated: %s; is the temperature too high: %s;is there any cell voltage violated: %s" % (
                status.isCMAVolVio, status.isCMATempVio, status.isCellVolVio))
        print("detectStatus End")

    # def setStatusToMessageObj(self, StatusObj, MessageObj):
    #     MessageObj.message_data_list.append(StatusObj.istempHigh);
    #     MessageObj.message_data_list.append(StatusObj.isvolLimited);
    #     MessageObj.message_data_list.append(StatusObj.isCVViolated);