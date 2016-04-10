

#CLS:xkozak15
import re
import sys
import xml.dom.minidom as minidom
from copy import copy, deepcopy
from lxml import etree
from pprint import pprint

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

        self.inherit_from = None
        self.inheritance_class_id = None


class Attr:
    def __init__(self, name, is_static=None, type=None, inheritance_class_id=None):
        self.type = type
        self.name = name
        self.is_static = is_static

        # class specified in "using" statement
        self.inheritance_class_id = inheritance_class_id

        self.inherit_from = None


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

    def to_xml_basic(self, root,output,indent_size=4):
        elem = self.__prepare_class_header()
        root.append(elem)

        for child in (x[1] for x in self.children):
            child.to_xml_basic(elem,output,indent_size)

        return prepare_xml_from_elem_tree(root,indent_size,True,output=output)

    def show_details(self,output=None,root=None,indent_size=4):

        elem = self.__prepare_class_header()
        if self.inherit:
            inherit_elem = etree.Element("inheritance")
            for cls in self.inherit:
                cls_elem = etree.Element("from")
                cls_elem.attrib["name"] = cls[1]
                cls_elem.attrib["privacy"] = InheritanceType.getStringForType(cls[0])
                inherit_elem.append(cls_elem)
            elem.append(inherit_elem)



        for type, str_repr in ((x, InheritanceType.getStringForType(x)) for x in InheritanceType.getTypes()):

            inner_elem = etree.Element(str_repr)
            not_empty = False

            for i in (self.attributes, "attributes"), (self.methods, "methods"):

                if i[0][type]:
                    if not not_empty:
                        not_empty = True

                    tmp = etree.Element(i[1])
                    inner_elem.append(tmp)
                    for attr in i[0][type]:
                        a = etree.Element(i[1][:-1])
                        a.attrib["name"] = attr.name
                        a.attrib["type"] = attr.type
                        a.attrib["scope"] = "class" if attr.is_static else "instance"
                        if attr.inheritance_class_id:
                            a.append(etree.Element("from", {"name": attr.inheritance_class_id}))
                        elif attr.inherit_from:
                            a.append(etree.Element("from", {"name": attr.inherit_from}))
                        if i[1] == "methods":
                            if attr.is_virtual:
                                virtual_elem = etree.Element("virtual",
                                                             {"pure": "yes" if attr.is_pure_virtual else "no"})
                                a.append(virtual_elem)

                            arguments = etree.Element("arguments")
                            if attr.params:
                                for param in attr.params:
                                    param_element = etree.Element("argument", {"name": param[1], "type": param[0]})
                                    arguments.append(param_element)
                            a.append(arguments)

                        tmp.append(a)

            if not_empty:
                elem.append(inner_elem)

        # attrs, methods = self.get_inherited_members()

        if root == None:
            return prepare_xml_from_elem_tree(elem,indent_size,True,output=output)
        else:
            root.append(elem)

    '''send attributes and methods to children (visibility according to the inheritance type)'''

    def send_members_to_children(self):
        if self.children:
            public_methods = deepcopy(self.methods[InheritanceType.public])
            protected_methods = deepcopy(self.methods[InheritanceType.protected])
            private_pure_virtual_methods = deepcopy(
                [x for x in self.methods[InheritanceType.private] if x.is_pure_virtual])

            public_attrs = deepcopy(self.attributes[InheritanceType.public])
            protected_attrs = deepcopy(self.attributes[InheritanceType.protected])

            for x in public_methods + protected_methods + private_pure_virtual_methods + public_attrs + protected_attrs:
                if not x.inherit_from:
                    x.inherit_from = self.name

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
                    raise BaseClsException("Unknown inheritance type")

                # now add the pure virtual methods
                child[1].methods[InheritanceType.private] += private_pure_virtual_methods
        if self.children:
            for child in [x[1] for x in self.children]:
                child.send_members_to_children()

        #make class abstract if it contains anything pure virtual
        self.check_abstract_x_concrete()

    def check_abstract_x_concrete(self):
        if self.__contains_pure_virtual_methods():
            self.kind = Cls.ABSTRACT
        else:
            self.kind = Cls.CONCRETE_CLASS

    def __contains_pure_virtual_methods(self):
        if self.methods:
            for i in self.methods.values():
                for m in i:
                    if m.is_pure_virtual:
                        return True
        else:
            return False

    def solve_all_using_statements(self):
        for x in self.attributes.values():
            for y in x:
                if y.inheritance_class_id:
                    self.__solve_using_statement(y)

    def get_parent_class(self, name):
        for x in [x[1] for x in self.parents]:
            if x.name == name:
                return x
            for y in [z[1] for z in x.parents]:
                ret = y.get_parent_class(name)
                if ret:
                    return ret
        return None

    def __solve_using_statement(self, attribute):
        cls = self.get_parent_class(attribute.inheritance_class_id)
        if not cls:
            raise BaseClsException("Given parent class " + attribute.inheritance_class_id + " was not found")

        parent_attr, access_modifier = cls.get_attribute(attribute.name)

        # remove the old reference from list, default location is private
        self.attributes[InheritanceType.private] = list(
            filter(lambda x: attribute.name != x.name, self.attributes[InheritanceType.private]))

        # now copy all useful info into subclass parameter
        attribute.type = parent_attr.type
        attribute.is_static = parent_attr.is_static
        attribute.inherit_from = parent_attr.inherit_from

        # now remove all other mambers with the same name
        for x in InheritanceType.getTypes():
            self.attributes[x] = list(filter(lambda x: attribute.name != x.name, self.attributes[x]))
            self.methods[x] = list(filter(lambda x: attribute.name != x.name, self.methods[x]))

        self.attributes[access_modifier].append(attribute)


    def get_attribute(self, name):
        for key, value in self.attributes.items():
            for y in value:
                if y.name == name:
                    return y, key
        raise BaseClsException("Attribute " + name + " was not found in class " + self.name)

    def check_conflicts(self):
        for x in InheritanceType.getTypes():
            for y in self.attributes[x] + self.methods[x]:
                others = self.get_members_with_name(y.name)
                if len(others) != 1:
                    methods = list(filter(lambda x: isinstance(x,Method),others))
                    for method in methods:
                        if not method.is_virtual:
                            raise BaseClsException("Inheritance conflict with member " + y.name)

    def get_members_with_name(self, name):
        res = []
        for x in InheritanceType.getTypes():
            for y in self.attributes[x] + self.methods[x]:
                    if y.name == name:
                        res.append(y)
        return res

    def check_pure_virtual_methods(self):
        for access_modifier in InheritanceType.getTypes():
            for y in self.methods[access_modifier]:
                if y.is_pure_virtual:
                    members_with_same_name = self.get_members_with_name(y.name)
                    methods_with_same_name = list(filter(lambda x: isinstance(x, Method), members_with_same_name))
                    if len(methods_with_same_name) >= 2:

                        # get rid of those inherited pure virtual methods
                        for method in methods_with_same_name:
                            if not method.is_pure_virtual and method.type == y.type:
                                # if the method is virtual, but not pure virtual and has the same return type, than we found implementation of pure virtual method, so the class may no longer be abstract
                                self.__remove_pure_virtual_method(method.name,access_modifier)
                                self.check_abstract_x_concrete()


    def __remove_pure_virtual_method(self,name,access_modifier):
        self.methods[access_modifier] = list(filter(lambda x : x.name != name and x.is_pure_virtual,self.methods[access_modifier]))



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
        line = line.strip()
        inheritance_class_id = None
        # check for using specification
        if line.startswith("using "):
            line = line.replace("using ", "")

            inheritance_class_id = re.findall("(.+)::.*", line)[0]
            line = line.replace(inheritance_class_id + "::", "")
            cls.add_attr(Attr(line, inheritance_class_id=inheritance_class_id), inheritance_type)
            return

        type, name = line.rsplit(" ", 1)

        for symbol in ("*","&"):
            while symbol in name:
                type = type + symbol
                name = name.replace(symbol," ")

        if "static " in type:
            type = type.replace("static ", "")
            is_static = True
        else:
            is_static = False

        type = type.strip()
        name = name.strip()

        cls.add_attr(Attr(type=type, name=name, is_static=is_static), inheritance_type)


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


def __make_classs_tag_openclose(string):
    string = string.group(0)
    indent = string.index("<class")
    return string.replace("/>", ">") + "\n" + indent * "\t" + "</class>"


def pretty_print_xml(string,indent_size,output=sys.stdout):
    data = minidom.parseString(string).toprettyxml(indent=indent_size * " ")
    tmp = data #re.sub(".*<class(.+?)/>", lambda m: __make_classs_tag_openclose(m), data)

    # now make arguments tag open close
    tmp = re.sub("<arguments/>", "<arguments></arguments>", tmp)
    tmp = tmp.replace("<?xml version=\"1.0\" ?>\n","")
    print("<?xml version=\"1.0\" encoding=\"UTF-8\"?>",file=output)
    print(tmp,file=output)


def prepare_xml_from_elem_tree(root_elem,indent_size,return_string=False,output=None):
    data = etree.tostring(root_elem)
    if return_string:
        return data
    else:
        pretty_print_xml(data,indent_size,output=output)
