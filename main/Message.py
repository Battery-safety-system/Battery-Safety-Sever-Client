class Message(object):
	"""docstring for Message"""
	def __init__(self, arg):
		super(Message, self).__init__()
		# exmaple: map: key: Hex number 181 e.g. value: (e.g. BMU01_pdo1)
        self.message_dbc = {};
        for i in range(1, 5):
            for j in range(1, 16):
                key_id = str(i) + '8' + str(hex(j))[2:];
                value_str = 'BMU' + str(j).zfill(2)+'_pdo' + str(i);
                self.message_dbc[int(key_id, 16)] = value_str;
        for i in range(5, 9):
            for j in range(1, 16):
                key_id = str(i - 4) + '9' + str(hex(j))[2:];
                value_str = 'BMU' + str(j).zfill(2)+'_pdo' + str(i);
                self.message_dbc[int(key_id, 16)] = value_str;
        self.reverse_message_dbc =  {v: k for k, v in self.message_dbc.items()}

    def getBatteryList(self):
    	pass;


    def getLabel(self):
        # 1.1 get the battery number
        self.sendSynMessage();
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

        # 1.2 get the req_message
        # example battery_list [1, 3]
        self.battery_list = list(set([int(elem[3:5]) for elem in label_list]));
        # Req_message_list = [BMU01_Req_send_message, BMU03_Req_send_message];
        #print([ eval('self.' + 'BMU'+str(battery_id).zfill(2)+'_Req_send_message') for battery_id in battery_list]);
        # print();
        self.Req_message_list = [];
        Req_list = ['self.' + 'BMU'+str(battery_id).zfill(2)+'_Req_send_message' for battery_id in self.battery_list];
        for ele in Req_list:
            print(ele)
            self.Req_message_list.append(eval(ele));
         
        
        # 1.3 get the total pdo number with Req sending
        self.sendSynMessage();
        self.sendReqMessage(self.Req_message_list);
        count = 0;
        self.label_list = [];
        message_dict = {}
        while True:
            message = self.bus.recv();
            if(message.arbitration_id not in self.message_dbc):
                count += 1;
        
            else:
                message_name = self.message_dbc[message.arbitration_id];
                message_dict[message_name] = message;
                self.label_list.append(message_name);
                count = 0;
            if(count > 10):
                break;
        self.label_list.sort(); #[BMU01_pdo01, BMU02_pdo02 ...]
        # print('label list')
        # print(self.label_list)
        logging.info(f'label list: {self.label_list}')

        # 1.4 construct the label list
        self.final_label_list = [] # BMU01_Max_temp, BMU01_Min_temp
        for label in self.label_list:
            A_message = message_dict[label];
            battery_name = label[0:5] #BMU01 or BMU02
            data_decode = self.db.decode_message(A_message.arbitration_id, A_message.data);
            for key, value in data_decode.items(): # key: Max_temp
                final_label = battery_name + '_' + key;
                self.final_label_list.append(final_label);
        self.final_label_list.sort();
        self.final_label_list.insert(0, 'time');
        self.final_label_list.insert(0, 'date'); # final_label_list: [date time BMU01_Max_temp .... BMU02_Max_temp ...]





        # self.temperature_voliated_battery = [];
		