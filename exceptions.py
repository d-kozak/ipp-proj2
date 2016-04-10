

#CLS:xkozak15
class BaseClsException(Exception):
    def __init__(self,__str):
        self.__str = __str + "\n"
    def __str__(self):
        return repr(self.__str)