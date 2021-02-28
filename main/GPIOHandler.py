
class GPIOHandler(object):
    """docstring for GPIOHandler"""
    def __init__(self, mode, GPIOInfoList):
        super(GPIOHandler, self).__init__()
        GPIO.setwarnings(False)
        GPIO.setmode(mode)# BCM 
        setGPIO(GPIOInfoList);

    def setGPIO(self, GPIOInfoList): # GPIO: device, pin_number, pin_type, pin_value
        for GPIOInfo in GPIOInfoList:
            print("set " + GPIOInfo["pin_number"])
            GPIO.setup(GPIOInfo["pin_number"], GPIOInfo["pin_type"])
            GPIO.output(GPIOInfo["pin_number"], GPIOInfo["pin_value"]);
