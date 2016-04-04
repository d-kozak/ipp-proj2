import sys
from enum import Enum

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


def print_help():
    print("Help me, please")
    sys.exit(1)


def error(msg, ret_val):
    print(msg, file=sys.stderr)
    sys.exit(ret_val)