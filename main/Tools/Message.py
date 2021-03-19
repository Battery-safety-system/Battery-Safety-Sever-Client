#!/usr/bin/python3
import cantools
import can

class Message(object):
    """docstring for Message"""
    def __init__(self):
        super(Message, self).__init__()
        print("Initialize Message Object")
        # exmaple: map: key: Hex number 181 e.g. value: (e.g. BMU01_pdo1)
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
        print("Message Object Initialization End")


    def getMessageDBC(self):
        message_dbc = {};
        for i in range(1, 5):
            for j in range(1, 16):
                key_id = str(i) + '8' + str(hex(j))[2:];
                value_str = 'BMU' + str(j).zfill(2)+'_pdo' + str(i);
                message_dbc[int(key_id, 16)] = value_str;
        for i in range(5, 9):
            for j in range(1, 16):
                key_id = str(i - 4) + '9' + str(hex(j))[2:];
                value_str = 'BMU' + str(j).zfill(2)+'_pdo' + str(i);
                message_dbc[int(key_id, 16)] = value_str;
        return message_dbc;

    def setReqMessage(self):
        for battery_id in range(1, 16):
            Req_Name = 'BMU' + str(battery_id).zfill(2)+'_SDO_Req';
            BMU_Req_Data = b'\x2F\x05\x18\x01\x00\x00\x00\x00';
            Req_message = 'BMU' + str(battery_id).zfill(2)+'_Req_send_message';
            message_content = self.db.get_message_by_name(Req_Name)
            setattr(self, Req_message, can.Message(arbitration_id= message_content.frame_id, data=BMU_Req_Data, extended_id=False));
        
    def setSyncMessage(self):
        sync = self.db.get_message_by_name('SYNC');
        sync_data = sync.encode({'Sync_Count':0xFF});
        self.sync_message = can.Message(arbitration_id = 0x80, data = sync_data, extended_id = False)

    def getReqMessageList(self):
        Req_message_list = [];
        Req_list = ['self.' + 'BMU'+str(battery_id).zfill(2)+'_Req_send_message' for battery_id in self.battery_list];
        for ele in Req_list:
            print(ele)
            Req_message_list.append(eval(ele));
        return Req_message_list;

