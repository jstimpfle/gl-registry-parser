#
# OpenGL Registry parser. No BS.
#
# Work in progress. Features are not yet supported.
#
# Feed gl.xml from Khronos into this. Change the code to generate the interface
# you need.
#

import sys
import xml.etree.ElementTree as ET

class GL_Enum:
    def __init__(self):
        self.name = None
        self.value = None
        self.group = None
    def __repr__(self):
        return 'ENUM {}={} group={}'.format(self.name, self.value, self.group)

class GL_Command:
    def __init__(self):
        self.name = None
        self.returntype = None
        self.params = []
    def __repr__(self):
        #return 'Command({}, {}, {})'.format(self.name, self.returntype, self.params)
        return 'COMMAND {} {}({});'.format(self.returntype, self.name,
                                ', '.join('{} {}'.format(tp, name)
                                            for (tp, name) in self.params))

class GL_Type:
    def __init__(self):
        self.name = None
        self.typedesc = None
    def __repr__(self):
        return 'TYPE {} {}'.format(self.typedesc, self.name)
        
def get_node_text(node):
    return ''.join(node.itertext())

def parse_type_node(node):
    tp = GL_Type()
    for typedesc in node.itertext():
        tp.typedesc = typedesc.strip()
        break
    for namenode in node:
        if namenode.tag == 'name':
            tp.name = get_node_text(namenode)
    print(tp)

def parse_enum_node(node):
    enum = GL_Enum()
    enum.name = node.attrib['name']
    enum.value = node.attrib['value']
    enum.group = node.attrib.get('group')
    print(enum)

def parse_command_node(node):
    cmd = GL_Command()
    if node.tag == 'command':
        for child in node:
            if child.tag == 'proto':
                for returntype in child.itertext():
                    cmd.returntype = returntype.strip()
                    break
                for protochild in child:
                    if protochild.tag == 'name':
                        cmd.name = get_node_text(protochild)
            elif child.tag == 'param':
                ptype, pname = None, None
                # sometimes the ptype is specified without enclosing <ptype>
                # tag. It might always be when the type is more complicated,
                # involving pointer indirection, but I don't understand this.
                for ptype in child.itertext():
                    ptype = ptype.strip()
                for paramchild in child:
                    if paramchild.tag == 'ptype':
                        ptype = get_node_text(paramchild)
                    elif paramchild.tag == 'name':
                        pname = get_node_text(paramchild)
                cmd.params.append((ptype, pname))
    print(cmd)

tree = ET.parse('gl.xml')
root = tree.getroot()
assert root.tag == 'registry'
for node in root:
    if node.tag == 'types':
        for typenode in node:
            parse_type_node(typenode)
    elif node.tag == 'enums':
        if ('namespace', 'GL') in node.attrib.items():
            for enumnode in node:
                if enumnode.tag == 'enum':
                    parse_enum_node(enumnode)
    elif node.tag == 'commands':
        if ('namespace', 'GL') in node.attrib.items():
            for commandnode in node:
                parse_command_node(commandnode)
