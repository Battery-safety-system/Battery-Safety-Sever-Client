int analogPin = A0; // potentiometer wiper (middle terminal) connected to analog pin 3
                    // outside leads to ground and +5V

int Temp1_PIN = 0;
int Temp2_PIN = 1;
int Pressure_PIN = 2;
int Current_PIN = 3;

// out pin
int PumpFan_PIN = 4;
int Relay1_PIN = 5;
int Relay2_PIN= 6;
int PrechargeRelay_PIN = 7;


void setup() {
  Serial.begin(9600);           //  setup serial
}

void loop() {
// step1
    int Temp1 = digitalRead(Temp1_PIN); //Reading the button state
    int Temp2 = digitalRead(Temp2_PIN); //Reading the button state
    int Pressure = digitalRead(Pressure_PIN); //Reading the button state
    int Current = digitalRead(Current_PIN); //Reading the button state

    String str_temp1 = "Temp1: ";
    String str1 = str_temp1  + Temp1 ; 
    
    String str_temp2 = ";Temp2: ";
    String str2 = str_temp2  + Temp2;

    String str_pre = ";Pressure: ";
    String str3= str_pre  + Pressure;

    String str_cur = ";Current: ";
    String str4 = str_cur  + Current;
    Serial.println(str1 + str2 + str3 + str4);


}
