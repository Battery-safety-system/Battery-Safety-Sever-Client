def fun1():
    try:
        1/0
    except Exception as e:
        raise Exception("fun1: " + str(e));

def fun2():
    try:
        fun1();
    except Exception as e:
        raise Exception("fun2: " + str(e));
def fun3():
    try:
        fun2();
    except Exception as e:
        print(e)
fun3();