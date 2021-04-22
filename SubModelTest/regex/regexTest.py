import re;
import json
# txt = "asdf}{""} {sdfas}"
# txt = "{asdfasd}"
# txt2 = "asdf"
# x = re.search(r"\s*{\s*}\s*", txt);
# x = re.search(r"\{(\s*)\}", txt)
dict1= {"abced" : "asdf", "aa": "bb"}
dict2= {"abced" : "asdf", "aa": "bb"}
dict_json = json.dumps(dict1).encode('utf-8') + json.dumps(dict2).encode('utf-8')[0: 2]
txt = dict_json.decode('utf-8')
print(type(txt))
x = re.search("\{(.+)\}", txt )
# x = re.search("{", txt)
list1 = re.findall("\{(.+)\}", txt)
content = "{" + list1[0] + "}";
dict_re = json.loads(content)
print(dict_re)
print(type(dict_re))
# print(list1[0])
# print(txt)
if x:
  print("YES! We have a match!")
else:
  print("No match")
