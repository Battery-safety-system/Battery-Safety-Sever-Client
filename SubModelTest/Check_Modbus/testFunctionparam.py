
def LoopIfNotMeetReq(handler, times, *args, **kwargs):

    for i in range(times):
        if(handler(*args)):
            return True;
    return False;





