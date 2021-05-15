from testFunctionparam import LoopIfNotMeetReq
#
# def LoopIfNotMeetReq(handler, times):
#
#     for i in range(times):
#         if(handler()):
#             return True;
#     return False;
class handlerObj:
    def __init__(self):
        self.var1 = 1;

    def handler(self):
        self.var1 += 1;
        print(self.var1)
        return False;

    def run(self, *args, **kwargs):
        LoopIfNotMeetReq(self.handler, 10)

o1 =handlerObj();
o1.run();