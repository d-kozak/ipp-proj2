import re
from globals import InheritanceType

class Cls:
    def __init__(self, name, inherit):
        self.name = name.replace(" ","")
        self.inherit = inherit

    def __str__(self):
        data = self.name + " " + " Inherit: "
        for cls in self.inherit:
            data += str(cls[0]) + " " + cls[1] + ","
        return repr(data[:-1])

def parse_inheritance_type(cls):
    type = None
    if " " in cls:
        tmp = cls.split(" ")
        print(tmp)
        type = InheritanceType.getTypeFromString(tmp[0])
        cls = tmp[1]
    else:
        type = InheritanceType.public

    return type,cls

def __parse_class(cls):
    # print(cls)

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


def parse_classes_from_file(args):
    file_content = args.input.read()

    classes = re.findall(r"class.+?};", file_content, re.DOTALL)

    ret_val = []

    for cls in classes:
        ret_val.append(__parse_class(cls))

    for cl in ret_val:
        print(str(cl))

    return ret_val
