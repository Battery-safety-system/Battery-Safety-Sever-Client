class PressTest:
    def __init__(self):
        pass

    def getPress(self, Volval):
        voltage = (Volval /1024.0 * 5.0);
        press = -1;
        if(voltage < 0.5) :
            press = 0;
        elif (voltage > 4.5):
            press = 150;
        else:
            press = (voltage - 0.5) /(4.5 - 0.5) * 150
        return  press;

        pass