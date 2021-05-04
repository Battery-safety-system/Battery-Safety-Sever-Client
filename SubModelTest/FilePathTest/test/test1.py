import pathlib
path = str(pathlib.Path().absolute())

# print(path)
# path2 = str(pathlib.Path(__file__).parent.absolute()) + "\\data.txt"

import sys
sys.path.append(path)

from  FileDir.FileRead import *;
#
fun1(str(path) + "\\test\\data.txt")

# txt = "aa" + "/aas"
# print(txt)
