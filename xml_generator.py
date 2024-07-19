from test_supremica_generator import *
import xml.etree.ElementTree as ET

pre_supremica = final_result

print(pre_supremica)

print(pre_supremica == final_result)

Module = ET.Element("Module", Name = "Casino-blocking")
EventDeclList = ET.SubElement(Module, "EventDeclList")
ComponentList = ET.SubElement(Module, "ComponentList")

# Here we are specifying the xmlns attribute that we have to add
xmlns_uris = {"":"http://waters.sourceforge.net/xsd/module",
    ':B':"http://waters.sourceforge.net/xsd/base"}

# This is a function to add the xmlns attribute to the root node which is "Module"
def add_XMLNS_attributes(tree, xmlns_uris_dict):
    if not ET.iselement(tree):
        tree = tree.getroot()
    for prefix, uri in xmlns_uris_dict.items():
        tree.attrib['xmlns' + prefix] = uri

add_XMLNS_attributes(Module, xmlns_uris)

for efsm in pre_supremica['Components']:
    SimpleComponent = ET.SubElement(ComponentList, "SimpleComponent", Name = efsm, Kind = "Plant")

print('______________________________________________________')

print(isinstance(Module, ET.Element))