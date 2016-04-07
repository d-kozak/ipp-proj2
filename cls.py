import sys
import pprint


from args_parser import Args
from class_parser import parse_classes_from_file,find_class_by_name,get_no_parent_classes

from lxml import etree

def print_basic_info(classes):
    root = etree.Element("model")
    for cls in get_no_parent_classes(classes):
        cls.to_xml_basic(root)

    txt = etree.tostring(root,pretty_print=True)
    print("<?xml version=\"1.0\" encoding=\"UTF-8\"?>\n" + str(txt))

def create_class_tree(classes):
    for cls in classes:
        for i in cls.inherit:
            parent_class = find_class_by_name(classes,i[1])

            parent_class.add_child(cls)
            cls.add_parent(parent_class)

    return  classes

def main():
    args = Args(sys.argv[1:])

    classes = parse_classes_from_file(args)

    create_class_tree(classes)

    pprint.pprint(classes)

    print_basic_info(classes)

if __name__ == "__main__":
    main()
