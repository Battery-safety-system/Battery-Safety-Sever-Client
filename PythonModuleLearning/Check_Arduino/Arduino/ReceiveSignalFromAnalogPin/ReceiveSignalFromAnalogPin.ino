int analogPin = A0; // potentiometer wiper (middle terminal) connected to analog pin 3
                    // outside leads to ground and +5V
int val = 0;  // variable to store the value read

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
    int test = 1 ;
    String str_temp1 = "Temp1: ";
    String str1 = str_temp1  + 1 ; 
    
    String str_temp2 = ";Temp2: ";
    String str2 = str_temp2  + 2;
    
    Serial.println(str1 + str2);
//    Serial.println(2);
//    Serial.println(3);
//    Serial.println(4);

  if (Serial.available() > 0){  //Looking for incoming data
    String incoming_state = Serial.readString();  //Reading the data
    int PumpFan = incoming_state.charAt(0) - '0';
    int Relay1 = incoming_state.charAt(1) - '0';
    int Relay2 = incoming_state.charAt(2) - '0';
    int PrechargeRelay = incoming_state.charAt(3) - '0';
    digitalWrite( PumpFan_PIN, PumpFan);  
    digitalWrite( Relay1_PIN, Relay1);  
    digitalWrite(Relay2_PIN, Relay2 );  
    digitalWrite(PrechargeRelay_PIN, PrechargeRelay);  
    Serial.println("GET THE VALUE");
  }

//  digitalWrite( 4, HIGH); 
  

}

//  val = analogRead(analogPin);  // read the input pin
//  String str = "send the bus";
//  Serial.println(str);          // debug value
//  int PumpFan = Serial.read();
////  int Relay1 = 
//  Serial.println(PumpFan); 
//  digitalWrite(PumpFan_PIN, PumpFan);  //Making the LED light up or down
//  digitalWrite(Relay1_PIN, Relay1);  //Relay2_PINMaking the LED light up or down

///  incoming_state = Serial.read() - '0';  //Reading the data
