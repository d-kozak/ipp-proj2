import re


class Cls:
    def __init__(self, name, inherit):
        self.name = name
        self.inherit = inherit

    def __str__(self):
        data = self.name + " " + " Inherit: "
        for cls in self.inherit:
            data += cls + ","
        return data[:-1]


def __parse_class(cls):
    # print(cls)

    header = re.findall("class(.+){.*", cls, re.DOTALL)[0]

    name = None
    inherit = []

    if ":" in header:  # if the class is inheritinng from someone
        tmp = header.split(":")
        name = tmp[0].replace(" ", "")
        for cls in tmp[1].split(","):
            inherit.append(cls.replace(" ", ""))

    else:
        name = header.replace(" ", "")

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
