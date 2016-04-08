import re
import sys
import xml.dom.minidom as minidom

from lxml import etree

from globals import InheritanceType
from exceptions import BaseClsException


class Method:
    def __init__(self):
        self.is_virtual = False
        self.is_pure_virtual = False
        self.is_static = False
        self.type = None
        self.name = None
        self.params = None


class Attr:
    def __init__(self, type, name, is_static):
        self.type = type
        self.name = name
        self.is_static = is_static


class Cls:
    CONCRETE_CLASS = "concrete"
    ABSTRACT = "abstract"

    def __init__(self, name, inherit, is_defined):
        self.name = name.replace(" ", "")
        self.inherit = inherit
        self.is_defined = is_defined
        self.attributes = {InheritanceType.public: [], InheritanceType.protected: [], InheritanceType.private: []}
        self.methods = {InheritanceType.public: [], InheritanceType.protected: [], InheritanceType.private: []}
        self.kind = Cls.CONCRETE_CLASS

        self.parents = []
        self.children = []

    def add_parent(self, p):
        self.parents.append(p)

    def add_child(self, c):
        self.children.append(c)

    def __repr__(self):
        data = self.name + "\n"

        if self.inherit:
            data += "\tInherit:\n"
            for cls in self.inherit:
                data += "\t\t" + str(cls[0]) + " " + cls[1] + "\n"

        if self.is_defined:
            data += "\tAttrs:\n"

            for x in self.attributes.values():
                for a in x:
                    data += "\t\t" + a.type + " " + a.name + "\n"

            data += "\tMethods:\n"
            for x in self.methods.values():
                for a in x:
                    data += "\t\t" + a.type + " " + a.name + " "
                    if a.params:
                        data += "Params: \n"
                        for p in a.params:
                            data += "\t\t" + p.type + " " + p.name + "\n"
        else:
            data += " \t -->is just DECLARED<--"

        return data

    def add_method(self, m, access_modifier):
        self.methods[access_modifier].append(m)

    def add_attr(self, a, access_modifier):
        self.attributes[access_modifier].append(a)

    '''check wheter class was defined, if not, define it using cls other'''

    def actualize(self, other):
        if not self.is_defined:
            self.attributes = other.get_attributes()
            self.methods = other.get_methods()
            self.is_defined = True

        else:
            raise BaseClsException("Redefininiton of class " + self.name)

    def __prepare_class_header(self):
        elem = etree.Element("class")
        elem.attrib["name"] = self.name
        elem.attrib["kind"] = self.kind
        return elem

    def to_xml_basic(self, root):
        elem = self.__prepare_class_header()
        root.append(elem)

        for child in (x[1] for x in self.children):
            child.to_xml_basic(elem)

        return etree.tostring(root, pretty_print=True)

    def show_details(self,root = None):
        elem = self.__prepare_class_header()
        if self.inherit:
            inherit_elem = etree.Element("inheritance")
            for cls in self.inherit:
                cls_elem = etree.Element("from")
                cls_elem.attrib["name"] = cls[1]
                cls_elem.attrib["privacy"] = InheritanceType.getStringForType(cls[0])
                inherit_elem.append(cls_elem)
            elem.append(inherit_elem)

        if self.is_defined:

            for type, str_repr in ((x, InheritanceType.getStringForType(x)) for x in InheritanceType.getTypes()):

                inner_elem = etree.Element(str_repr)
                elem.append(inner_elem)

                for i in (self.attributes, "attributes"), (self.methods, "methods"):

                    if i[0][type]:
                        tmp = etree.Element(i[1])
                        inner_elem.append(tmp)
                        for attr in i[0][type]:
                            a = etree.Element(i[1][:-1])
                            a.attrib["name"] = attr.name
                            a.attrib["type"] = attr.type
                            a.attrib["scope"] = "class" if attr.is_static else "instance"
                            if i[1] == "methods":
                                if attr.is_virtual:
                                    virtual_elem = etree.Element("virtual",{"pure":"yes" if attr.is_pure_virtual else "no"})
                                    a.append(virtual_elem)
                            tmp.append(a)

        # attrs, methods = self.get_inherited_members()

        if root == None:
            return etree.tostring(elem, xml_declaration=True, encoding='UTF-8')
        else:
            root.append(elem)

    '''send attributes and methods to children (visibility according to the inheritance type)'''

    def send_members_to_children(self):
        if self.children and self.is_defined:
            public_methods = self.methods[InheritanceType.public]
            protected_methods = self.methods[InheritanceType.protected]

            public_attrs = self.attributes[InheritanceType.public]
            protected_attrs = self.attributes[InheritanceType.protected]

            for child in self.children:
                if child[0] == InheritanceType.private:
                    child[1].attributes[InheritanceType.private] += public_attrs + protected_attrs
                    child[1].methods[InheritanceType.private] += public_methods + protected_methods
                elif child[0] == InheritanceType.protected:
                    child[1].attributes[InheritanceType.protected] += public_attrs + protected_attrs
                    child[1].methods[InheritanceType.protected] += public_methods + protected_methods
                elif child[0] == InheritanceType.public:
                    child[1].attributes[InheritanceType.public] += public_attrs
                    child[1].attributes[InheritanceType.protected] += protected_attrs
                    child[1].methods[InheritanceType.public] += public_methods
                    child[1].methods[InheritanceType.protected] += protected_methods
                else:
                    raise BaseClsException("Unknow inheritance type")
        if self.children:
            for child in [x[1] for x  in self.children]:
                child.send_members_to_children()

    '''TODO: delete this'''
    def get_inherited_members(self):
        attrs = []
        methods = []

        if self.parents:
            for i in self.parents:
                if i[1].is_defined:
                    attrs_public = i[1].attributes[InheritanceType.public]
                    attrs_protected = i[1].attributes[InheritanceType.protected]

                    methods_public = i[1].methods[InheritanceType.public]
                    methods_protected = i[1].methods[InheritanceType.protected]

                    if i[0] == InheritanceType.private:
                        for x in attrs_public + attrs_protected + methods_public + methods_protected:
                            x.visibility = InheritanceType.private
                    elif i[0] == InheritanceType.protected:
                        for x in attrs_public + attrs_protected + methods_public + methods_protected:
                            x.visibility = InheritanceType.protected
                    else:
                        for x in attrs_public + methods_public:
                            x.visibility = InheritanceType.public
                        for x in attrs_protected + methods_protected:
                            x.visibility = InheritanceType.protected

                    for x in attrs_public + attrs_protected + methods_public + methods_protected:
                        x.parent_cls = i[1]

                    attrs += attrs_protected + attrs_public
                    methods += methods_protected + methods_public

                    x, y = i[1].get_inherited_members()

                    attrs += x
                    methods += y

        return attrs, methods


'''parse the type of inheritance, default is public'''


def parse_inheritance_type(cls):
    inherit_type = None
    if " " in cls:
        tmp = cls.split(" ")
        inherit_type = InheritanceType.getTypeFromString(tmp[0])
        cls = tmp[1]
    else:
        inherit_type = InheritanceType.private

    return inherit_type, cls


'''parse inheritance from class header'''


def __parse_inheritance(cls):
    header = re.findall("class(.+){.*", cls, re.DOTALL)[0]

    name = None
    inherit = []

    if re.match(r"class(.+){\w*};", cls, re.DOTALL):
        is_defined = False
    else:
        is_defined = True

    if ":" in header:  # if the class is inheritinng from someone
        tmp = header.split(":")
        name = tmp[0]
        for cls in tmp[1].split(","):
            inherit.append(parse_inheritance_type(cls.strip()))

    else:
        name = header

    return Cls(name, inherit, is_defined)


def __check_visibility_type(line, inheritance_type):
    for inherit_id in InheritanceType.getTupleOfTypes():
        if inherit_id[1] in line:
            line = line.replace(inherit_id[1], "")
            inheritance_type = inherit_id[0]
            break
    return line, inheritance_type


'''parse all methods and attributes from class data'''


def __parse_method(cls, line, inheritance_type):
    method = Method()
    if "virtual" in line:
        line = line.replace("virtual", "")
        method.is_virtual = True

    if "=0" in line:
        line = line.replace("=0", "")
        if method.is_virtual:
            method.is_pure_virtual = True
        else:
            raise BaseClsException("Only virtual methods can be specified as pure virtual")

    if "static" in line:
        line = line.replace("static", "")
        method.is_static = True

    type, name, params = re.findall(r"(.*) (.*)\((.*)\).*", line, re.DOTALL)[0]

    method.type = type.strip()
    method.name = name.strip()

    param_list = []
    if params != "void" and params:
        for param in params.split(","):
            if param:
                ret_type, name = param.rsplit(" ", 1)
                param_list.append((ret_type, name))

    method.params = param_list
    cls.add_method(method, inheritance_type)


def __parse_attr(cls, line, inheritance_type):
    if line:
        type, name = line.rsplit(" ", 1)

        if "static " in type:
            type = type.replace("static ", "")
            is_static = True
        else:
            is_static = False

        type = type.strip()
        name = name.strip()

        cls.add_attr(Attr(type, name, is_static), inheritance_type)


def __is_method(line):
    return re.match(".*\(.*\).*", line, re.DOTALL)


def __parse_methods_and_attributes(cls, class_body):
    inheritance_type = InheritanceType.private

    for line in class_body.split(";"):
        if line:
            line, inheritance_type = __check_visibility_type(line, inheritance_type)
            line = line.replace("\n", "")
            if __is_method(line):
                __parse_method(cls, line, inheritance_type)
            else:
                __parse_attr(cls, line, inheritance_type)


'''parse one class from file,includes parsing inheritance,methods and parameters'''


def __parse_class(data):
    cls = __parse_inheritance(data)

    # now parse the body
    class_body = re.findall("{(.+)}", data, re.DOTALL)

    if not class_body:
        # if it was just a declaration
        cls.attributes = None
        cls.methods = None
        return cls
    else:
        __parse_methods_and_attributes(cls, class_body[0])

    for i in cls.methods.values():
        for m in i:
            if m.is_pure_virtual:
                cls.kind = Cls.ABSTRACT
                break

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


def find_class_by_name(classes, name):
    for cls in classes:
        if cls.name == name:
            return cls
    raise BaseClsException("Parent class of " + name + " not found")


def get_no_parent_classes(classes):
    ret_val = []
    for cls in classes:
        if not cls.parents:
            ret_val.append(cls)
    return ret_val


def pretty_print_xml(string):
    print(minidom.parseString(string).toprettyxml())