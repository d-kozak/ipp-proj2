import argparse
import sys

from globals import error, RetVal


class PrintHelp(argparse.Action):
    def __call__(self, *args, **kwargs):
        print("help")


class Args:
    NOT_SPECIFIED= "%__not specified"
    ALL="%__ALL"
    def __init__(self, arguments):
        super().__init__()

        self.__process_args(arguments)
        self.__check_args()

    def __process_args(self, arguments):

        parser = argparse.ArgumentParser(description="C++ header analysis toool")

        parser.add_argument('--help1',action=PrintHelp,help="Prints help")
        parser.add_argument("--input",type=argparse.FileType("r"),default=sys.stdin)
        parser.add_argument("--output",type=argparse.FileType("w"),default=sys.stdout)
        parser.add_argument("--pretty-xml", nargs="?", const=4, default=Args.NOT_SPECIFIED)
        parser.add_argument("--details", nargs="?", const=Args.ALL, default=Args.NOT_SPECIFIED)
        parser.add_argument("--search", nargs="?", const="%IDK", default=Args.NOT_SPECIFIED)
        parser.add_argument("--conflicts", nargs="?", const="%IDK", default=Args.NOT_SPECIFIED)

        parser.parse_args(arguments,Args)

    def __check_args(self):
        if self.conflicts != Args.NOT_SPECIFIED and self.details == Args.NOT_SPECIFIED:
            error("--conflicts must be set with --details",RetVal.WRONG_ARGS)

        if self.search != Args.NOT_SPECIFIED:
            if self.details != Args.NOT_SPECIFIED or self.conflicts != Args.NOT_SPECIFIED:
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
