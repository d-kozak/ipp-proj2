import sys
from enum import Enum
from exceptions import BaseClsException

class RetVal(Enum):
    EOK = 0
    WRONG_ARGS = 1
    WRONG_INPUT_FILE = 2
    WRONG_OUTPUT_FILE = 3
    WRONG_PRETTY_XML_VAL = 4
    ERR_SEMANTIC = 5

class Operation(Enum):
    CLASSIC = 0
    SHOW_CLASS = 1

class InheritanceType(Enum):
    public = 0
    protected = 1
    private = 2

    @staticmethod
    def getTypes():
        return [InheritanceType.private,InheritanceType.protected,InheritanceType.public]

    @staticmethod
    def getTypeFromString(string):

        #empty == no modifier = public
        if not string:
            return "public"
        if string == "public":
            return InheritanceType.public
        elif string == "protected":
            return InheritanceType.protected
        elif string == "private":
            return InheritanceType.private
        else:
            raise BaseClsException("Unknown access modifier: " +string)

    @staticmethod
    def getStringForType(type):
        if type == InheritanceType.public:
            return "public"
        elif type == InheritanceType.protected:
            return "protected"
        elif type == InheritanceType.private:
            return "private"
        else:
            raise BaseClsException("Unknown member visibility type")

    @staticmethod
    def getTupleOfTypes():
        return [(InheritanceType.public,"public:"),(InheritanceType.protected,"protected:"),(InheritanceType.private,"private:")]


def error(msg, ret_val):
    print(msg, file=sys.stderr)
    sys.exit(ret_val)