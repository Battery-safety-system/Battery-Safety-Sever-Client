#define INPUT_SIZE 30
// get info
int Temp1_PIN = A0;
int Temp2_PIN = A1;
int Press_PIN = A2;
int test_PIN = A3;
// set value
int Pump_PIN = 7;
int Fan_PIN = 6;

int Relay1_PIN = 5;
int Relay2_PIN = 3;
int Relay3_PIN = 4;

void setup() {
  // put your setup code here, to run once:
  Serial.begin(9600);  //Started the serial communication at 9600 baudrate
  // Input PIN
  pinMode(Temp1_PIN, INPUT);
  pinMode(Temp2_PIN, INPUT);
  pinMode(Press_PIN, INPUT);
  // output PIN
  pinMode(Pump_PIN, OUTPUT);
  pinMode(Relay1_PIN, OUTPUT);
  pinMode(Relay2_PIN, OUTPUT);
  pinMode(Relay3_PIN, OUTPUT);
  pinMode(Fan_PIN, OUTPUT);
  
  digitalWrite( Pump_PIN, 0);
  digitalWrite( Relay1_PIN, 0);
  digitalWrite( Relay2_PIN, 0);
  digitalWrite( Relay3_PIN, 0);
  digitalWrite( Fan_PIN, 0);
//  Serial.setTimeout(100); // set new value to 100 milliseconds

}

void loop() {
  // put your main code here, to run repeatedly:
  int Temp1 = analogRead(Temp1_PIN);
  int Temp2 = analogRead(Temp2_PIN);
  int Press = analogRead(Press_PIN);
  int test = analogRead(test_PIN);
  // send mapStatus to Rasp
  String mapStatus = "Ardu_Temp1:" + String(Temp1) + ",Ardu_Temp2:" + String(Temp2) + ",Ardu_Press:" + String(Press) ;
  Serial.println(mapStatus);
  
  delay(500);
  if(Serial.available() != 0) {
    char input[INPUT_SIZE + 1];
    byte size = Serial.readBytes(input, INPUT_SIZE);
    // Add the final 0 to end the C string
    input[size] = 0;
    char* command = strtok(input, "&");
    while (command != 0)
    {
    // Split the command in two values
      char* separator = strchr(command, ':');
      if (separator != 0)
      {
       // Actually split the string in 2: replace ':' with 0
           *separator = 0;
           int servoId = atoi(command);
           ++separator;
           int val = atoi(separator);
           digitalWrite( servoId, val);
       // Do something with servoId and position
      }
       // Find the next command in input string
      command = strtok(0, "&");
   }
 }



}
