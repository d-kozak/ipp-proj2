import sys
from args_parser import Args
from class_parser import parse_classes_from_file

from lxml import etree

def print_basic_info(classes):
    root = etree.Element("model")
    for cls in classes:
        cls.to_xml_basic(root)

    txt = etree.tostring(root,pretty_print=True)
    print(txt)

def main():
    args = Args(sys.argv[1:])

    classes = parse_classes_from_file(args)


    print_basic_info(classes)

if __name__ == "__main__":
    main()
