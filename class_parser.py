import re
from globals import InheritanceType
from lxml import etree


class Method:
    def __init__(self):
        self.is_virtual = False
        self.is_pure_virtual = False
        self.is_static = False
        self.type = None
        self.name = None
        self.params = None

class Attr:
    def __init__(self,type,name):
        self.type = type
        self.name = name


class Cls:
    def __init__(self, name, inherit):
        self.name = name.replace(" ", "")
        self.inherit = inherit
        self.is_defined = False
        self.attrs = []
        self.methods = []
        self.kind = "concrete"

    def __str__(self):
        data = self.name + " " + " Inherit: "
        for cls in self.inherit:
            data += str(cls[0]) + " " + cls[1] + ","
        return repr(data[:-1])

    def add_method(self,m):
        self.methods.append(m)

    def add_attr(self,a):
        self.attrs.append(a)

    '''check wheter class was defined, if not, define it using cls other'''

    def actualize(self, other):
        if not self.is_defined:
            self.attrs = other.get_attributes()
            self.methods = other.get_methods()
            self.is_defined = True

        else:
            raise BaseException("Redefininiton of class " + self.name)

    def to_xml_basic(self, root):
        elem = etree.Element("class")
        elem.text = self.name
        elem.attrib["name"] = self.name
        elem.attrib["kind"] = self.kind
        root.append(elem)
        return etree.tostring(root,pretty_print=True)


'''parse the type of inheritance, default is public'''


def parse_inheritance_type(cls):
    inherit_type = None
    if " " in cls:
        tmp = cls.split(" ")
        inherit_type = InheritanceType.getTypeFromString(tmp[0])
        cls = tmp[1]
    else:
        inherit_type = InheritanceType.public

    return inherit_type, cls


'''parse inheritance from class header'''


def __parse_inheritance(cls):
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


def __check_visibility_type(line, inheritance_type):
    for inherit_id in InheritanceType.getTupleOfTypes():
        if inherit_id[1] in line:
            line = line.replace(inherit_id[1], "")
            inheritance_type = inherit_id[0]
            break
    return line, inheritance_type


'''parse all methods and attributes from class data'''


def __parse_method(cls, line):
    method = Method()
    if "virtual" in line:
        line = line.replace("virtual", "")
        method.is_virtual = True

    if "=0" in line:
        line = line.replace("=0", "")
        if method.is_virtual:
            method.is_pure_virtual = True
        else:
            raise BaseException("Only virtual methods can be specified as pure virtual")

    if "static" in line:
        line = line.replace("static", "")
        method.is_static = True

    type, name, params = re.findall(r"(.*) (.*)\((.*)\).*", line, re.DOTALL)[0]

    method.type = type
    method.name = name

    param_list = []
    if params != "void" and params:
        for param in params.split(","):
            if param:
                ret_type, name = param.rsplit(" ",1)
                param_list.append((ret_type, name))

    method.params = param_list
    return method

def __parse_attr(cls, line):
    if line:
        type,name = line.rsplit(" ",1)

        type = type.strip()
        name = name.strip()

        a = Attr(type,name)
        cls.add_attr(a)


def __is_method(line):
    return re.match(".*\(.*\).*", line, re.DOTALL)


def __parse_methods_and_attributes(cls, class_body):
    inheritance_type = InheritanceType.private

    for line in class_body.split(";"):
        if line:
            line, inheritance_type = __check_visibility_type(line, inheritance_type)
            line = line.replace("\n", "")
            if __is_method(line):
                cls.add_method(__parse_method(cls, line))
            else:
                __parse_attr(cls, line)


'''parse one class from file,includes parsing inheritance,methods and parameters'''


def __parse_class(data):
    cls = __parse_inheritance(data)

    # now parse the body
    class_body = re.findall("{(.+)}", data, re.DOTALL)

    if not class_body:
        # if it was just a declaration
        cls.attrs = None
        cls.methods = None
        return cls
    else:
        __parse_methods_and_attributes(cls, class_body[0])

    return cls


'''parses classes from input file specified in class args'''


def parse_classes_from_file(args):
    file_content = args.input.read()

    classes = re.findall(r"class.+?};", file_content, re.DOTALL)

    ret_val = []

    for cls in classes:
        new_class = __parse_class(cls)
        if new_class.name not in [x.name for x in ret_val]:
            ret_val.append(new_class)
        else:
            cls = [x for x in ret_val if x.name == new_class.name][0]
            cls.actualize(new_class)

    return ret_val
