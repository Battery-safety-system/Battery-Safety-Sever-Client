void setup() {
  // put your setup code here, to run once:
  Serial.begin(9600);  
}

void loop() {
  // put your main code here, to run repeatedly:
  String incoming_state;
//  if (Serial.available() > 0){
//    
//    
//  }
  incoming_state = Serial.readString();
  Serial.println(incoming_state);
}
