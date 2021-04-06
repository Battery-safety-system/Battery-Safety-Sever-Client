import inspect


class Number:
    # Class Attributes
    def __init__(self):
        self.isWarning = True;
        self.isDangerous = True;
        self.isPossible = True;
        self.iP = True;
    def show(self):
        for i in inspect.getmembers(self):
            if not i[0].startswith('_') and i[0].startswith('is'):
                if not inspect.ismethod(i[1]):
                    print(i[1])
    def setFalse(self):
        for i in inspect.getmembers(self):
            if not i[0].startswith('_') and i[0].startswith('is'):
                if not inspect.ismethod(i[1]):
                    setattr(self, i[0], False)
# Driver's code
n = Number()
# for i in inspect.getmembers(n):
#
#     # to remove private and protected
#     # functions
#     if not i[0].startswith('_') and i[0].startswith('is'):
#
#         # To remove other methods that
#         # doesnot start with a underscore
#         if not inspect.ismethod(i[1]):
#             print(i)
n.setFalse();
n.show();