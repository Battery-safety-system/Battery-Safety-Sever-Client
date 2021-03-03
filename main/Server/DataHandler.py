class DataHandler(object):
	"""docstring for DataHandler"""
	def __init__(self):
		super(DataHandler, self).__init__()
	
	def getLabelFromDict(self, content):
		assert isinstance(content, dict)
		assert list(content.keys())[0] == "Label"
		return content["Label"];


	def getDataFromDict(self, content):
		assert isinstance(content, dict)
		assert list(content.keys())[0] == "Data"
		return content["Data"];

	def getStatusFromDict(self, content):
		assert isinstance(content, dict)
		assert list(content.keys())[0] == "Status"
		return content["Status"];

	# def printList

	def getDeviceInfoString(self, status):
        str1="Device: Pump is "
        if(status[0] == True):
            str1 += "on"
        else:
            str1 += "off"
        str1 += " Relay is "
        if(status[1] == True or status[2] == True):
            str1 += "off"
        else :
            str1 += "on"
        return str1;

    def getStatusInfoString(self, status):
        str1="status: isvolLimited: " +  str(status[0]) + "istempHigh: " +  str(status[1]) + "isCVViolated: " +  str(status[2])
        
        return str1;