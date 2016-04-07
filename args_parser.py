import getopt
import sys

from globals import error, print_help, RetVal


class Args:
    def __init__(self, arguments):
        super().__init__()
        self.__process_args(arguments)

    def __process_args(self, arguments):
        long_opts = ["help", "input=", "output=", "pretty-xml=", "details=", "search=", "conflicts"]

        try:
            optlist, args = getopt.getopt(arguments, [], long_opts)
        except getopt.GetoptError as err:
            error(str(err),RetVal.WRONG_ARGS)



        if len(args) != 0:
            error("Too many arguments", RetVal.WRONG_ARGS)

        self.__parse_args(optlist)
        self.__check_args()

    def __parse_args(self, optlist):
        self.input = sys.stdin
        self.output = sys.stdout
        self.pretty_xml = False
        self.details = False
        self.search = False
        self.conflicts = False

        for opt, val in optlist:
            if opt == "--help":
                print_help()
            elif opt == "--input":
                try:
                    self.input = open(val)
                except FileNotFoundError:
                    error("Cant open input file", RetVal.WRONG_INPUT_FILE)
            elif opt == "--output":
                try:
                    self.output = open(val,"w")
                except FileNotFoundError:
                    error("Cant open output file", RetVal.WRONG_OUTPUT_FILE)
            elif opt == "pretty-xml":
                try:
                    self.pretty_xml = int(val)
                except TypeError:
                    error("Value specified for pretty-xml is not a number", RetVal.WRONG_PRETTY_XML_VAL)
            elif opt == "--details":
                self.details = val if val != "" else True
            elif opt == "--search":
                self.search = val
            elif opt == "--conflicts":
                self.conflicts = val

    def __check_args(self):
        if self.conflicts != False and self.details == False:
            error("--conflicts must be set with --details",RetVal.WRONG_ARGS)

        if self.search != False:
            if self.details != False or self.conflicts != False:
                error("--search must be set alone", RetVal.WRONG_ARGS)

    def getInput(self):
        return self.input

    def getOutput(self):
        return self.output

    def getPrettyXml(self):
        return self.pretty_xml

    def getDetails(self):
        return self.details

    def getSearch(self):
        return self.search

    def getConflicts(self):
        return self.conflicts
