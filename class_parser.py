import re
from globals import InheritanceType


class Cls:
    def __init__(self, name, inherit):
        self.__name = name.replace(" ", "")
        self.__inherit = inherit
        self.__is_defined = False
        self.__attrs = None
        self.__methods = None

    def __str__(self):
        data = self.__name + " " + " Inherit: "
        for cls in self.__inherit:
            data += str(cls[0]) + " " + cls[1] + ","
        return repr(data[:-1])

    def set_attributes(self, attributes):
        self.__attrs = attributes

    def set_methods(self, methods):
        self.__methods = methods

    def get_name(self):
        return self.__name

    def get_inherit(self):
        return self.__inherit

    def get_attributes(self):
        return self.__attrs

    def get_methods(self):
        return self.__methods

    '''check wheter class was defined, if not, define it using cls other'''
    def actualize(self,other):
        if not self.__is_defined:
            self.__attrs = other.get_attributes()
            self.__methods = other.get_methods()
            self.__is_defined = True


'''parse the type of inheritance, default is public'''
def parse_inheritance_type(cls):
    type = None
    if " " in cls:
        tmp = cls.split(" ")
        type = InheritanceType.getTypeFromString(tmp[0])
        cls = tmp[1]
    else:
        type = InheritanceType.public

    return type, cls


'''parse inheritance from class header'''
def __parse_iheritance(cls):
    header = re.findall("class(.+){.*", cls, re.DOTALL)[0]

    name = None
    inherit = []

    if ":" in header:  # if the class is inheritinng from someone
        tmp = header.split(":")
        name = tmp[0]
        for cls in tmp[1].split(","):
            inherit.append(parse_inheritance_type(cls.strip()))

    else:
        name = header

    return Cls(name, inherit)

'''parse one class from file,includes parsing inheritance,methods and parameters'''
def __parse_class(data):
    cls = __parse_iheritance(data)

    # now parse the body
    class_body = re.findall("{(.+)}",data,re.DOTALL)

    if not class_body:
        # if it was just a declaration
        cls.set_attributes(None)
        cls.set_methods(None)
        return  cls

    

    return cls

'''parses classes from input file specified in class args'''
def parse_classes_from_file(args):
    file_content = args.input.read()

    classes = re.findall(r"class.+?};", file_content, re.DOTALL)

    ret_val = []

    for cls in classes:
        new_class = __parse_class(cls)
        if new_class.get_name() not in [x.get_name() for x in ret_val]:
            ret_val.append(new_class)
        else:
            cls = [x for x in ret_val if x.get_name() == new_class.get_name()][0]
            cls.actualize(new_class)

    for cl in ret_val:
        print(str(cl))

    return ret_val
