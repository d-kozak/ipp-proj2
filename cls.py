import sys
from exceptions import BaseClsException
from pprint import pprint


from args_parser import Args
from class_parser import parse_classes_from_file,find_class_by_name,get_no_parent_classes,pretty_print_xml,prepare_xml_from_elem_tree

from lxml import etree

def print_basic_info(classes):
    root = etree.Element("model")
    for cls in get_no_parent_classes(classes):
        cls.to_xml_basic(root)

    prepare_xml_from_elem_tree(root)



def create_class_tree(classes):
    for cls in classes:
        for i in cls.inherit:
            parent_class = find_class_by_name(classes,i[1])

            parent_class.add_child((i[0],cls))
            cls.add_parent((i[0],parent_class))

    for cls in get_no_parent_classes(classes):
        cls.send_members_to_children()

    return  classes

def main():
    args = Args(sys.argv[1:])

    classes = parse_classes_from_file(args)
    create_class_tree(classes)

    #pprint(classes)

    if args.details != Args.NOT_SPECIFIED:
        #true means all
        root = etree.Element("model")
        if args.details == Args.ALL:
            for cls in classes:
                cls.show_details(root)
            prepare_xml_from_elem_tree(root)
        #otherwise it contains class name
        else:
            try:
                pretty_print_xml(find_class_by_name(classes,args.details).show_details())
            except BaseClsException:
                # if the class does not exists, print just the header
                args.getOutput().write("<?xml version=\"1.0\" encoding=\"utf-8\"?>")

    else:
        print_basic_info(classes)

if __name__ == "__main__":
    main()
