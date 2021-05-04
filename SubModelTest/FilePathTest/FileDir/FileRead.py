import pathlib
path = pathlib.Path().absolute()
print("FileRead: " + str(path))
def fun1(file):
    print(str(pathlib.Path(__file__).parent.absolute()))
    with open(file, 'r') as f:
        data = f.read()
        print(data)