void setup() {
  // put your setup code here, to run once:
  Serial.begin(9600);  
}

void loop() {
  // put your main code here, to run repeatedly:
  String incoming_state;
  incoming_state = Serial.readString();
//  if(incoming_state == "") {
//    return;
//    } 
  Serial.println(incoming_state);

}
