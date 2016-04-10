

#CLS:xkozak15
class BaseClsException(Exception):
    def __init__(self,__str):
        self.__str = __str
    def __str__(self):
        return repr(self.__str)