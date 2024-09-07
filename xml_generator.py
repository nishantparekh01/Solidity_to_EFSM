from add_events_nodes import *
import xml.etree.ElementTree as ET
from datetime import datetime
import os


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

#############################################################################################################

# Adding variable 'value' to the VariableComponent

VariableComponent_value = ET.Element("VariableComponent",  Name = "value")

VariableRange_value = ET.SubElement(VariableComponent_value, "VariableRange")
BinaryExpression_value = wmodify_assignment("0", "..", "1")
VariableRange_value.append(BinaryExpression_value)
# BinaryExpression_value = ET.SubElement(VariableRange_value, "BinaryExpression", Operator = "..")
# IntConstant_value_0 = ET.SubElement(BinaryExpression_value, "IntConstant", Value = "0")
# IntConstant_value_1 = ET.SubElement(BinaryExpression_value, "IntConstant", Value = "1")

VariableInitial_value = ET.SubElement(VariableComponent_value, "VariableInitial")
BinaryExpression_value_init = wmodify_assignment("value", "==", "0")
VariableInitial_value.append(BinaryExpression_value_init)

# used wmodify_assignment function to create the BinaryExpression instead of code below
# BinaryExpression_value_init = ET.SubElement(VariableInitial_value, "BinaryExpression", Operator = "==")
# SimpleIdentifier_value = ET.SubElement(BinaryExpression_value_init, "SimpleIdentifier", Name = "value")
# IntConstant_value_init = ET.SubElement(BinaryExpression_value_init, "IntConstant", Value = "0")

ComponentList.append(VariableComponent_value)

#############################################################################################################

# Adding variable 'sender' to the VariableComponent

VariableComponent_sender = ET.Element("VariableComponent",  Name = "sender")
VariableRange_sender = ET.SubElement(VariableComponent_sender, "VariableRange")
EnumSetExpression_sender = ET.SubElement(VariableRange_sender, "EnumSetExpression")

sender_list = VariableComponent ['AddressVariables']
# sender_list is a dictionary of address variables
# {'operator': 'x0001', 'player': 'x0002'}

for address in sender_list.values():
    EnumSetExpression_sender.append(ET.Element("SimpleIdentifier", Name = address))

# adding initial value to 'sender'
VariableInitial_sender = ET.SubElement(VariableComponent_sender, "VariableInitial")
BinaryExpression_sender_init = wmodify_assignment("sender", "==", "x0001")
VariableInitial_sender.append(BinaryExpression_sender_init)

ComponentList.append(VariableComponent_sender)

#############################################################################################################

# Adding transfer efsm for each address variable





#############################################################################################################


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

timestamp = datetime.now().strftime("%Y_%m_%d_%H_%M")


# Define the folder where you want to store the output files
base_folder = r'C:\Users\nishantp\OneDrive - Chalmers\Casino\Casino_Nishant\casino\Output test files'


# Create a unique folder name using the current timestamp
output_folder = os.path.join(base_folder, f"output_{timestamp}")

# Create new output folder
os.makedirs(f"{output_folder}")


# Generate a unique filename using the current timestamp
filename = os.path.join(base_folder, f"{output_folder}\\output_{timestamp}.wmod")

# Text file containing a short summary of changes made
filename_txt = os.path.join(base_folder,f"{output_folder}\\output_{timestamp}.txt")


# Open the file and write the output
with open(filename, 'w') as file:
    print(ET.tostring(Module, encoding='utf8').decode('utf8'), file=file)

summary = (""" Able to achieve transition for transfer_fail. from the node where transfer takes place. Thank god !!!
""")

with open(filename_txt, 'w') as file:
    print(summary, file=file)

print(f"Output written to {output_folder}")

#print(ET.tostring(Module, encoding='utf8').decode('utf8'))