import csv
class testTemp:
    def __init__(self):
        self.getDictFromSensorCsv();
        pass
    def getDictFromSensorCsv(self):
        ohmsList = [];
        tempList = [];
        with open('TempSensor.csv', newline='') as csvfile:
            spamreader = csv.reader(csvfile, delimiter=',')
            for row in spamreader:
                ohms = int(row[1]);
                temp = int(row[0])
                ohmsList.append(ohms)
                tempList.append(temp)
        self.tempList = tempList
        self.ohmsList = ohmsList;
        pass
    
    
    def convertTempToRealValue(self, Volval):
        voltage = (Volval /1024.0 * 5.0)
        print(voltage)
        ohms = (2200 * voltage) / (5.0 - voltage)
        for i in range(1, len(self.ohmsList)):
            val = self.ohmsList[i];
            if (val >= ohms ) :
                topline = val;
                bottomline =  self.ohmsList[i - 1]
                if(bottomline > ohms):
                    return 140;
                per = (ohms - bottomline)/(topline - bottomline)
                temp_high = self.tempList[i - 1];
                temp_low = self.tempList[i];
                temp = (temp_high - temp_low) * per + temp_low;
                return temp
                pass
        return -1; 

        pass
t1 = testTemp();
print(t1.convertTempToRealValue(584))