#define INPUT_SIZE 30
int Temp1_PIN = 0;
int Pump_PIN = 4; 
int Relay_PIN = 5; 
void setup() {
  // put your setup code here, to run once:
  Serial.begin(9600);  //Started the serial communication at 9600 baudrate
  pinMode(Temp1_PIN, INPUT);
  pinMode(Pump_PIN, OUTPUT);
  pinMode(Relay_PIN, OUTPUT);
  Serial.println("Arduino Start");

}

void loop() {
  // put your main code here, to run repeatedly:
  int Temp1 = digitalRead(Temp1_PIN);
  // send mapStatus to Rasp
  String mapStatus = "Temp1:" + String(Temp1);
  Serial.println(mapStatus);

  if (Serial.available() > 0){
    // get data from rasp
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


    // active device
//     digitalWrite( Pump_PIN, Pump);
//     digitalWrite( Relay_PIN, Relay);
  }
}
