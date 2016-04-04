import sys
from args_parser import Args
from class_parser import parse_classes_from_file

def main():
    args = Args(sys.argv[1:])

    parse_classes_from_file(args)


if __name__ == "__main__":
    main()
