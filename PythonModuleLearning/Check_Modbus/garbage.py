#     def LoopIfNotMeetReq(self, handler, times, *args, **kwargs):
#         try:
#             for i in range(times):
# #                 print("LoopIfNotMeetReq: " + handler.__name__ + ": " + str(i) + " times")
#                 time.sleep(1);
#                 if (handler(*args)):
#                     return True;
#         except:
#             print("loop not meet req")
#             raise Exception(handler.__name__ + " cannot work even after " + str(times) + " times");
#         finally:
#             return False;

# section2
# for i in range(10):
#     time.sleep(1);
#     if (self.checkModbusIfInit()):
#         break;



#         ## Read voltage set point(Init value) ##
#         self.instrument.write_register(41026, self.voltage_mode, 0, 6)  # K_op_mode
#         voltage = self.instrument.read_register(41027, 0) / self.voltage_scale
#         print("The Initial voltage is ", str(voltage), "Volts")