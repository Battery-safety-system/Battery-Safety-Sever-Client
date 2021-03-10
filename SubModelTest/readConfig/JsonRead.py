import json

with open('JsonTest1') as f:
  data = json.load(f)
data
# Output: {'name': 'Bob', 'languages': ['English', 'Fench']}
print(type(data))
print(data)