from add_events_nodes import *
import xml.etree.ElementTree as ET

# pre_supremica is imported from add_events_nodes.py
# pre_supremica is in the form of a dictionary

#print(pre_supremica)

Module = ET.Element("Module", Name = "Casino-blocking")

# Adding the EventDeclList to the Module
xml_EventDecl = pre_supremica['Events']
Module.append(xml_EventDecl)

# Adding event Name = ":accepting", kind = "PROPOSITION" to the EventDeclList
EventDecl_accepting = ET.SubElement(xml_EventDecl, "EventDecl", Kind = "PROPOSITION", Name = ":accepting")


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




# Loop to add VariableComponent
for var, val in pre_supremica['Components']['VariableComponent'].items():
    #VariableComponent = ET.SubElement(ComponentList, "VariableComponent",  Name = var)
    #print(var)
    #print('-----------------')
    if not isinstance(val, dict):
        xml_VariableComponent = pre_supremica['Components']['VariableComponent'][var]
        #print(str(xml_VariableComponent))
        ComponentList.append(xml_VariableComponent)

# Adding variable 'value' to the VariableComponent

VariableComponent_value = ET.Element("VariableComponent",  Name = "value")

VariableRange_value = ET.SubElement(VariableComponent_value, "VariableRange")
BinaryExpression_value = ET.SubElement(VariableRange_value, "BinaryExpression", Operator = "..")
IntConstant_value_0 = ET.SubElement(BinaryExpression_value, "IntConstant", Value = "0")
IntConstant_value_1 = ET.SubElement(BinaryExpression_value, "IntConstant", Value = "1")

VariableInitial_value = ET.SubElement(VariableComponent_value, "VariableInitial")
BinaryExpression_value_init = ET.SubElement(VariableInitial_value, "BinaryExpression", Operator = "==")
SimpleIdentifier_value = ET.SubElement(BinaryExpression_value_init, "SimpleIdentifier", Name = "value")
IntConstant_value_init = ET.SubElement(BinaryExpression_value_init, "IntConstant", Value = "0")

ComponentList.append(VariableComponent_value)




for efsm in pre_supremica['Components']:
    SimpleComponent = None
    if efsm != 'VariableComponent':
        if efsm == "":
            efsm = ""
            #global SimpleComponent
            SimpleComponent = ET.SubElement(ComponentList, "SimpleComponent",  Kind = "PLANT",Name = efsm)
        else:
            #global SimpleComponent
            SimpleComponent = ET.SubElement(ComponentList, "SimpleComponent",  Kind = "PLANT", Name = efsm)

        Graph = ET.SubElement(SimpleComponent, "Graph")
        #NodeList = ET.SubElement(Graph, "NodeList")
        #EdgeList = ET.SubElement(Graph, "EdgeList")

        xml_NodeList = pre_supremica['Components'][efsm]['node_list']
        xml_EdgeList = pre_supremica['Components'][efsm]['edge_list']

        Graph.append(xml_NodeList)
        Graph.append(xml_EdgeList)




print('______________________________________________________')


print(ET.tostring(Module, encoding='utf8').decode('utf8'))