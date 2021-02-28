

// In pin
int Temp1_PIN = 0;
int Temp2_PIN = 1;
int Pressure_PIN = 2;
int Current_PIN = 3;

// out pin
int PumpFan_PIN = 4;
int Relay1_PIN = 5;
int Relay2_PIN= 6;
int PrechargeRelay_PIN = 7;


void setup(){
  Serial.begin(9600);  //Started the serial communication at 9600 baudrate

  pinMode(Temp1, INPUT); //Declaring button pin as the input pin.
  pinMode(Temp2, INPUT); //Declaring button pin as the input pin.
  pinMode(Pressure, INPUT); //Declaring button pin as the input pin.
  pinMode(Current, INPUT); //Declaring button pin as the input pin.

  pinMode(PumpFan, OUTPUT); //Declaring led pin as output pin
  pinMode(Relay1, OUTPUT); //Declaring led pin as output pin
  pinMode(Relay2, OUTPUT); //Declaring led pin as output pin
  pinMode(PrechargeRelay, OUTPUT); //Declaring led pin as output pin

}

void loop(){
    // step1
    int Temp1 = digitalRead(Temp1_PIN); //Reading the button state
    int Temp2 = digitalRead(Temp2_PIN); //Reading the button state
    int Pressure = digitalRead(Pressure_PIN); //Reading the button state
    int Current = digitalRead(Current_PIN); //Reading the button state
    // step2
    // create a string map
    String mapStatus = "Temp1" + ":" + std::to_string(Temp1) + ", ";
    String mapStatus = "Temp2" + ":" + std::to_string(Temp2) + ", ";
    String mapStatus = "Pressure" + ":" + std::to_string(Temp1) + ", ";
    String mapStatus = "Current" + ":" + std::to_string(Temp1) ;

    // step3: transfer the map
    Serial.println("Arduino: Prepare for Arduino Communication");
    if(Serial.readString() != b'Rasp: I\'m OK') {
        Serial.println("Arduino: There is Error, Stop this loop Please");
        // log
     }

     Serial.println(mapStatus);

    // step4: get the control signal
    String controlMap = Serial.readString();
    Serial.println("Arduino: Received Control Map");
        // control signal handling
    int PumpFan = 0;
    int Relay1 = 0;
    int Relay2 = 0;
    int PrechargeRelay = 0;


    // step5: use the control signal
    digitalWrite(PumpFan_PIN, PumpFan);  //Making the LED light up or down
    digitalWrite(Relay1_PIN, Relay1);  //Relay2_PINMaking the LED light up or down
    digitalWrite(Relay2_PIN, Relay2);  //Making the LED light up or down
    digitalWrite(PrechargeRelay_PIN, PrechargeRelay);  //Making the LED light up or down


}
// prepare jobs
// Function I need:
// button_state = digitalRead(button_pin);
// digitalWrite(pin, val);
// Serial.println

// logic behind it:
// step1: get temp1, temp2, temp3
// step2: transfer them to via Serial to the PC
// step3: PC receive the data and then send the command to the Arduino
// step4: the command is to control the pump+fan, relay, precharge relay
// step5: Arduino use the digitalWrite to write the data, another loop

// Take care:
// how to sync the rasp with arduino: using the Serial read, because Serial reading will block the programmar pointer, Arduino will wait unitl rasp reply
// I recommand to write a json file to control all the thing, read all the data, and control all the data by json format.

// ref:
// reading String: http://elextutorial.com/learn-arduino/arduino-serial-read-string-line-from-serial-monitor-readstring-function/
// stoi: https://www.geeksforgeeks.org/converting-strings-numbers-cc/
// write: https://www.arduino.cc/reference/en/language/functions/communication/serial/write/
// main file: https://electronicshobbyists.com/control-arduino-using-raspberry-pi-arduino-and-raspberry-pi-serial-communication/
// map to String: http://www.cplusplus.com/forum/general/211386/
// int to string: http://www.cplusplus.com/reference/string/to_string/


//
