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


VariableInitial_value = ET.SubElement(VariableComponent_value, "VariableInitial")
BinaryExpression_value_init = wmodify_assignment("value", "==", "0")
VariableInitial_value.append(BinaryExpression_value_init)

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
# Ideally this value should be the one which is assigned in the constructor of the contract
VariableInitial_sender = ET.SubElement(VariableComponent_sender, "VariableInitial")
BinaryExpression_sender_init = wmodify_assignment("sender", "==", "x0001")
VariableInitial_sender.append(BinaryExpression_sender_init)

ComponentList.append(VariableComponent_sender)

#############################################################################################################

# Replacing address domain for all address variables
# Do we have an address list ?:
print(AddressVariables)

for address_name, address_value in VariableComponent['AddressVariables'].items():
    if address_name in VariableComponent:
        print(f'Updating address: {address_name}')

        # Get the VariableComponent for the address
        xml_VariableComponent = VariableComponent[address_name]

        # Remove existing VariableRange (if required)
        existing_ranges = xml_VariableComponent.findall("VariableRange")
        for existing_range in existing_ranges:
            xml_VariableComponent.remove(existing_range)

        # Remove existing VariableInitial (to ensure correct order when re-adding)
        existing_initial = xml_VariableComponent.find("VariableInitial")
        if existing_initial is not None:
            xml_VariableComponent.remove(existing_initial)

        # Add VariableRange first
        xml_variableRange = ET.SubElement(xml_VariableComponent, "VariableRange")
        xml_EnumSetExpression = ET.SubElement(xml_variableRange, "EnumSetExpression")

        # Copy the EnumSetExpression from sender
        for child in EnumSetExpression_sender:
            xml_EnumSetExpression.append(ET.Element("SimpleIdentifier", Name=child.attrib["Name"]))

        # Add VariableInitial second
        xml_VariableInitial = ET.SubElement(xml_VariableComponent, "VariableInitial")
        xml_initialValue = wmodify_assignment(address_name, "==", address_value)
        xml_VariableInitial.append(xml_initialValue)

#############################################################################################################

# Print the updated VariableComponent for verification
# for address_name, xml_component in VariableComponent.items():
#     print(f"Updated VariableComponent for {address_name}:")
#     ET.dump(xml_component)

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

#############################################################################################################

# Adding assignSender from string format to xml
file_path_assignSender = r'assignSender_casino_blocking.xml'
assignSender_string = ET.parse(file_path_assignSender)


CASINO_NONBLOCKING ='smart_contracts/casino_nonblocking.sol'
ESCROW_BLOCKING = 'smart_contracts/escrow_v2_blocking.sol'
ESCROW_NONBLOCKING = 'smart_contracts/escrow_v2_nonblocking.sol'

if contract_file == CASINO_NONBLOCKING:
    print('casino_nonblocking')
    file_path_assignSender = r'assignSender_casino_nonblocking.xml'
    assignSender_string = ET.parse(file_path_assignSender)
elif contract_file == ESCROW_BLOCKING:
    print('escrow_blocking')
    file_path_assignSender = r'assignSender_escrow_blocking.xml'
    assignSender_string = ET.parse(file_path_assignSender)
elif contract_file == ESCROW_NONBLOCKING:
    print('escrow_nonblocking')
    file_path_assignSender = r'assignSender_escrow_nonblocking.xml'
    assignSender_string = ET.parse(file_path_assignSender)


ComponentList.append(assignSender_string.getroot())
add_events_to_xml('assignSev')




print('______________________________________________________')
print( Supremica)
#print(VariableComponent['AddressVariables'])
#print(transfer_efsm_list)
#print(asdf)


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

summary = (""" Adding the eventtransferX and eventtransferFail events to EventDecl list
""")

with open(filename_txt, 'w') as file:
    print(summary, file=file)

print(f"Output written to {output_folder}")


#print(ET.tostring(Module, encoding='utf8').decode('utf8'))