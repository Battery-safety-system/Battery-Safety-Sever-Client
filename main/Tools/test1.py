import json
import sys
sys.path.append("/home/pi/Desktop/Battery-Safety-Sever-Client")
with open('config.properties') as f:
    data = json.load(f)
data = data['ArduinoHandler']
print(data)
#         self.pumpPIN = data["pumpPIN"];
#         self.FanPIN = data["FanPIN"];
Relay1PIN = data["Relay1PIN"];
Relay2PIN = data["Relay2PIN"];
Relay3PIN = data["Relay3PIN"];