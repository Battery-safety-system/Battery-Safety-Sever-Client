from Message import Message;
import can
class PcanConnection(object):
    """docstring for PcanConnection"""
    def __init__(self):
        super(PcanConnection, self).__init__()
        
        #### ip address
        print("Initialize PCAN Connection")
        bustype = 'socketcan'
        channel = 'can0'
        self.bus = can.interface.Bus(channel=channel, bustype=bustype)

        print("PCAN Connection Initialization end");


    def sendMessage(self, message):
        print("Send Message: " + str(message.arbitration_id))
        self.bus.send(message);
        print("sendMessage() end");
        
    def sendMessageList(self, messageList):
        print("send Message list id: " + str([message.arbitration_id for message in messageList]))
        for Req_message in messageList:
            self.bus.send(Req_message);
        print("sendMessageList() end");

    def getBatteryListFromPcan(self, messageObj):
        print("Begin getBatteryListFromPcan()")
        battery_list = [];
        self.sendMessage(messageObj.sync_message);
        count = 0;
        label_list = [];
        while True:
            message = self.bus.recv();
            if(message.arbitration_id not in messageObj.message_dbc):
                count += 1;
            else:
                message_name = messageObj.message_dbc[message.arbitration_id];
                label_list.append(message_name);
                count = 0;
            if(count > 10):
                break;
        # label shoud be sorted [BMU01_pdo01, BMU02_pdo02 ...]
        label_list.sort();
        battery_list = list(set([int(elem[3:5]) for elem in label_list]));
        messageObj.battery_list = battery_list;
        print("getBatteryListFromPcan() end");
        
    def getLabelListPlusMessageDictFromPcan(self, messageObj):
        print("Begin getLabelListPlusMessageDictFromPcan()")
                # 1.3 get the total pdo number with Req sending
        self.sendMessage(messageObj.sync_message);
        self.sendMessageList(messageObj.Req_message_list);
        count = 0;
        label_list = [];
        message_dict = {}
        while True:
            message = self.bus.recv();
            if(message.arbitration_id not in messageObj.message_dbc):
                count += 1;
            else:
                message_name = messageObj.message_dbc[message.arbitration_id];
                message_dict[message_name] = message;
                label_list.append(message_name);
                count = 0;
            if(count > 10):
                break;
        label_list.sort(); #[BMU01_pdo01, BMU02_pdo02 ...]

        messageObj.label_list = label_list;
        messageObj.message_dict = message_dict;
        print("getLabelListPlusMessageDictFromPcan() end");

    def getFinalLabelList(self, messageObj):
        print("Begin getFinalLabelList()")
        final_label_list = [] # BMU01_Max_temp, BMU01_Min_temp
        for label in messageObj.label_list:
            A_message = messageObj.message_dict[label];
            battery_name = label[0:5] #BMU01 or BMU02
            data_decode = messageObj.db.decode_message(A_message.arbitration_id, A_message.data);
            for key, value in data_decode.items(): # key: Max_temp
                final_label = battery_name + '_' + key;
                final_label_list.append(final_label);
        final_label_list.sort();
        final_label_list.insert(0, 'time');
        final_label_list.insert(0, 'date'); # final_label_list: [date time BMU01_Max_temp .... BMU02_Max_temp ...]
        final_label_list.append('istempHigh'); final_label_list.append('isvolLimited');final_label_list.append('isCVViolated'); 
        messageObj.final_label_list = final_label_list;
        print("getFinalLabelList() end");

    def getDataFromPcan(self, messageObj):
        print("Begin getDataFromPcan()")
        self.sendMessage(messageObj.sync_message);
        self.sendMessageList(messageObj.Req_message_list)
        message_dict = {};
        count = 0;
        while True:
            message = self.bus.recv();
            if(message.arbitration_id not in messageObj.message_dbc ):
                count += 1;
                if(count > 10 and len(message_dict) != 0):
                    break;
                continue;
            message_name = messageObj.message_dbc[message.arbitration_id]
            message_dict[message_name] = message;
            count = 0;
        messageObj.message_dict = message_dict; 

        print("getDataFromPcan() end");

    def getReqMessageList(self, messageObj):
        print("Begin getReqMessageList()")
        messageObj.Req_message_list = messageObj.getReqMessageList();
        print("ReqMessage List id: ")
        print([ Req_message.arbitration_id  for Req_message in messageObj.Req_message_list]);
        print("ReqMessage List: " + str(messageObj.Req_message_list))
        print("getReqMessageList() end");

    def getAllInfo(self, messageObj):
        print("Begin getAllInfo()")
        # 1.1 get the battery number
        self.getBatteryListFromPcan(messageObj);
        self.getReqMessageList(messageObj);
        self.getLabelListPlusMessageDictFromPcan(messageObj)

        print(f'label list: {messageObj.label_list}')

        # 1.4 construct the label list
        self.getFinalLabelList(messageObj);
        print("getAllInfos() end");
