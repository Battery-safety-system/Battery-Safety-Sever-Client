#!/usr/bin/python3


class Status(object):
    """docstring for Status"""
    def __init__(self):
        super(Status, self).__init__()
        print("Initializae Status")
        # pcan status
        self.temperature_voliated_battery = [];
        self.battery_cell_voltage_voilated = [];

        self.isCMATempVio = False;
        self.isCMAVolVio = False;
        self.isCellVolVio = False;

        # Arduino status
        # "Ardu_Temp1": 36, "Ardu_Temp2": 37, "Ardu_Press": 100
        self.isArduTempHigh = False
        self.isArduPressViolated = False
        # modbus status
        self.isModbusCurrentViolated = False;
        self.isModbusVoltageViolated = False;
        self.isModbusPowerViolated = False

        self.warning = False;
        self.dangerous = False
    def getStatusDatas(self):
        return [self.isCMAVolVio, self.isCMATempVio, self.isCellVolVio, self.isArduTempHigh, self.isArduPressViolated, self.isModbusCurrentViolated, self.isModbusVoltageViolated, self.isModbusPowerViolated, self.warning, self.dangerous]

    def getLabels(self):
        return ["pcan_isCMATempVio", "pcan_isCMAVolVio", "pcan_isCellVolVio", "pcan_isArduTempHigh", "pcan_isArduPressViolated", "pcan_isModbusCurrentViolated", "pcan_isModbusVoltageViolated", "pcan_isModbusPowerViolated", "warning", "dangerous"];