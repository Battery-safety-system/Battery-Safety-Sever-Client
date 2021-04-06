import json

with open('../../main/Client/config.properties') as f:
  data = json.load(f)

print(int(data["pumpPIN"]))
# print(type(data))
# print(data)