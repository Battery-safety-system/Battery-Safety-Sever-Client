
def LoopIfNotMeetReq(handler, times, *args, **kwargs):

    for i in range(times):
        if(handler(*args)):
            return True;
    return False;

def systemOut(mess, mess2):
    print(mess)
    print(mess2)
mess = "get the book"
mess2 = 2
LoopIfNotMeetReq(systemOut, 10, mess, mess2)
# class test:
#     def __init__(self):
#         raise Exception("Error !!");
#     def __del__(self):
#         print("is right")
#
# # t1 = test();
# print( -1 + 2**32)