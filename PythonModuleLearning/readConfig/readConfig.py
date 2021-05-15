import json

with open('config.properties') as f:
  data = json.load(f)
data
# Output: {'name': 'Bob', 'languages': ['English', 'Fench']}
print(type(data))
print(data)


# Device: Pump Relay
# PIN: 18 16
# INIT_VAlUE: LOW HIGH
# GPIO_Mode: BCM
# BUS_TYPE: socketcan
# PORT_CHANNEL: 'can0'
# DBC_FILE: 'Goodwood_15BMUs_IFSpecV3_Node.dbc'