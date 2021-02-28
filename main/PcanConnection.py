from Message import Message;
class PcanConnection(object):
	"""docstring for PcanConnection"""
	def __init__(self, arg):
		super(PcanConnection, self).__init__()
        #### ip address
        print("Start CAN Bus Setting")
        bustype = 'socketcan'
        channel = 'can0'
        self.bus = can.interface.Bus(channel=channel, bustype=bustype)
        ### sync message setting
        print("Complete CAN Bus Setting")

    def sendMessage(self, message):
        self.bus.send(message);
        
    def sendMessageList(self, messageList):
        for Req_message in messageList:
            self.bus.send(Req_message);


    def getBatteryListFromPcan(self, messageObj):
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
        
    def getLabelListPlusMessageDictFromPcan(self, messageObj):
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

    def getFinalLabelList(self, messageObj):

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
        messageObj.final_label_list = final_label_list;

    def getDataFromPcan(self, messageObj):
        print("Begin getDataFromPcan()")
        sendMessage(messageObj.sync_message);
        sendMessageList(messageObj.Req_message_list)
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

	def getAllInfo(self, messageObj):
        # 1.1 get the battery number
        self.getBatteryListFromPcan(messageObj);

        self.getLabelListPlusMessageDictFromPcan(messageObj)

        logging.info(f'label list: {messageObj.label_list}')

        # 1.4 construct the label list
        self.getFinalLabelList(self, messageObj);

