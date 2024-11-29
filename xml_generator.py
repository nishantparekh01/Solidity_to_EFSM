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


# Constants used:
ONE = "1"
EVENT_END = "X"
EVENT_FAIL = "Fail"

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

# # Adding assignSender from string format to xml
# file_path_assignSender = r'assignSender_casino_blocking.xml'
# assignSender_string = ET.parse(file_path_assignSender)
#
#
# CASINO_NONBLOCKING ='smart_contracts/casino_nonblocking.sol'
# ESCROW_BLOCKING = 'smart_contracts/escrow_v2_blocking.sol'
# ESCROW_NONBLOCKING = 'smart_contracts/escrow_v2_nonblocking.sol'
#
# if contract_file == CASINO_NONBLOCKING:
#     print('casino_nonblocking')
#     file_path_assignSender = r'assignSender_casino_nonblocking.xml'
#     assignSender_string = ET.parse(file_path_assignSender)
# elif contract_file == ESCROW_BLOCKING:
#     print('escrow_blocking')
#     file_path_assignSender = r'assignSender_escrow_blocking.xml'
#     assignSender_string = ET.parse(file_path_assignSender)
# elif contract_file == ESCROW_NONBLOCKING:
#     print('escrow_nonblocking')
#     file_path_assignSender = r'assignSender_escrow_nonblocking.xml'
#     assignSender_string = ET.parse(file_path_assignSender)
#
#
# ComponentList.append(assignSender_string.getroot())
# add_events_to_xml('assignSev')

#############################################################################################################

# Build AssignMsg component

def count_statements_in_edge_list(supremica_data):
    """
    Identifies functions with `node_list` and `edge_list` where `edge_list` has more than one statement.

    :param supremica_data: The input data structure containing `node_list` and `edge_list`.
    :return: A dictionary with function names as keys and the count of statements in their `edge_list` as values.
    """
    components = supremica_data.get("Components", {})
    functions_with_multiple_statements = {}

    # Iterate through functions in components
    for function_name, details in components.items():
        if isinstance(details, dict) and "node_list" in details and "edge_list" in details:
            # Parse the edge_list XML
            edge_list = details["edge_list"]
            # Simulate parsing <Edge> elements (ensure edge_list is valid XML)
            edge_elements = ET.ElementTree(edge_list).findall("./Edge")
            edge_count = len(edge_elements)  # Count <Edge> elements

            # Check if there is more than one statement
            if edge_count > 1:
                functions_with_multiple_statements[function_name] = edge_count

    return functions_with_multiple_statements


# List of events ending with one for functions with more than on statement in edge_list

def extract_events_ending_with(edge_list, suffix):
    """
    Extracts events from the edge_list that end with the digit 1.

    :param edge_list: The edge_list XML element.
    :return: A list of event names ending with '1'.
    """
    events = set()
    print(edge_list)
    for edge in ET.ElementTree(edge_list).findall("./Edge/LabelBlock/SimpleIdentifier"):
        event_name = edge.get("Name")
        if event_name and event_name.endswith(suffix):
            if event_name not in events:
                events.add(event_name)
    return events


#############################################################################################################




print('______________________________________________________')
print( Supremica)

#############################################################################################################

# Get list of functions

function_list = []

for node in sol_list:
    if node['nodeType'] == 'FunctionDefinition' and node['visibility'] == 'public':
        #print(node['name'])
        if node['name'] != '':
            function_list.append(node['name'])

print(function_list)

# # assignMsg_result = count_statements_in_edge_list(Supremica)
# # print("Functions with more than one statement in edge_list:", assignMsg_result)
#
# # Step 1: Identify functions with more than one statement
# functions_with_multiple_statements = count_statements_in_edge_list(Supremica)
# print("Functions with more than one statement in edge_list:", functions_with_multiple_statements.keys())
#
# # Step 2: Extract events ending with '1' from edge_lists
# events_ending_with_1 = set()
# for function_name in functions_with_multiple_statements.keys():
#     events_ending_with_1.update(extract_events_ending_with(Supremica["Components"][function_name]["edge_list"], ONE))
#
# events_ending_with_1 = list(events_ending_with_1)
#
# # Step 2: Extract events ending with 'X' from edge_lists
# events_ending_with_X = set()
# for function_name in functions_with_multiple_statements.keys():
#     events_ending_with_X.update(extract_events_ending_with(Supremica["Components"][function_name]["edge_list"], EVENT_END))
#
# events_ending_with_X = list(events_ending_with_X)
#
# # Step 2: Extract events ending with 'Fail' from edge_lists
# events_ending_with_Fail = set()
# for function_name in functions_with_multiple_statements.keys():
#     events_ending_with_Fail.update(extract_events_ending_with(Supremica["Components"][function_name]["edge_list"], EVENT_FAIL))
#
# events_ending_with_Fail = list(events_ending_with_Fail)

def find_events_with_s0(supremica_data, function_names):

    components = supremica_data.get("Components", {})
    source_s0_events = set()  # Use set to ensure uniqueness
    target_s0_events = set()  # Use set to ensure uniqueness

    # Iterate through the provided function names
    for function_name in function_names:
        # Check if the function exists in Supremica components
        if function_name in components:
            details = components[function_name]
            if isinstance(details, dict) and "edge_list" in details:
                # Parse the edge_list XML
                edge_list = details["edge_list"]
                edges = list(ET.ElementTree(edge_list).findall("./Edge"))

                # Skip functions with one or zero edges
                if len(edges) <= 1:
                    continue

                # Process edges
                for edge in edges:
                    # Check if the edge has Source='S0'
                    if edge.get("Source") == "S0":
                        for event in edge.findall("./LabelBlock/SimpleIdentifier"):
                            source_s0_events.add(event.get("Name"))

                    # Check if the edge has Target='S0'
                    if edge.get("Target") == "S0":
                        for event in edge.findall("./LabelBlock/SimpleIdentifier"):
                            target_s0_events.add(event.get("Name"))

    return list(source_s0_events), list(target_s0_events)

source_s0, target_s0 = find_events_with_s0(Supremica, function_list)
print("Events with source 'S0':", source_s0)
print("Events with target 'S0':", target_s0)

#############################################################################################################

# Generate the XML structure for assignMsg component
def generate_address_xml(address_list):

    if not address_list:
        raise ValueError("Address list cannot be empty.")

    # Start with the first address as the initial root of the expression
    current = ET.Element("BinaryExpression", {"Operator": "=="})

    # Add sender' == first_address
    unary_expression = ET.SubElement(current, "UnaryExpression", {"Operator": "'"})
    ET.SubElement(unary_expression, "SimpleIdentifier", {"Name": "sender"})
    ET.SubElement(current, "SimpleIdentifier", {"Name": address_list[0]})

    # For each subsequent address, create a new BinaryExpression with an OR ('|') operator
    for address in address_list[1:]:
        new_root = ET.Element("BinaryExpression", {"Operator": "|"})
        new_root.append(current)

        right_expression = ET.SubElement(new_root, "BinaryExpression", {"Operator": "=="})
        unary_expression = ET.SubElement(right_expression, "UnaryExpression", {"Operator": "'"})
        ET.SubElement(unary_expression, "SimpleIdentifier", {"Name": "sender"})
        ET.SubElement(right_expression, "SimpleIdentifier", {"Name": address})

        # Update the current root
        current = new_root

    # Return the generated tree as a string
    return    current
address_xml = generate_address_xml(list(sender_list.values()))

def generate_assignMsg_efsm(source_s0, target_s0):

    # Create the root element
    root = ET.Element("SimpleComponent", Kind="PLANT", Name="assignMsg")

    # Create the Graph element
    graph = ET.SubElement(root, "Graph")

    # Create NodeList
    node_list = ET.SubElement(graph, "NodeList")

    # Add SimpleNode S0
    s0_node = ET.SubElement(node_list, "SimpleNode", Initial="true", Name="S0")
    event_list = ET.SubElement(s0_node, "EventList")
    ET.SubElement(event_list, "SimpleIdentifier", Name=":accepting")
    point_geom = ET.SubElement(s0_node, "PointGeometry")
    ET.SubElement(point_geom, "Point", X="208", Y="128")
    label_geom = ET.SubElement(s0_node, "LabelGeometry", Anchor="NW")
    ET.SubElement(label_geom, "Point", X="0", Y="10")

    # Add SimpleNode S1
    s1_node = ET.SubElement(node_list, "SimpleNode", Name="S1")
    event_list = ET.SubElement(s1_node, "EventList")
    ET.SubElement(event_list, "SimpleIdentifier", Name=":accepting")
    point_geom = ET.SubElement(s1_node, "PointGeometry")
    ET.SubElement(point_geom, "Point", X="496", Y="304")
    label_geom = ET.SubElement(s1_node, "LabelGeometry", Anchor="NW")
    ET.SubElement(label_geom, "Point", X="0", Y="10")

    # Create EdgeList
    edge_list = ET.SubElement(graph, "EdgeList")

    # Add edges for source S0 -> S1
    if source_s0:
        edge = ET.SubElement(edge_list, "Edge", Source="S0", Target="S1")
        label_block = ET.SubElement(edge, "LabelBlock")
        for event in source_s0:
            ET.SubElement(label_block, "SimpleIdentifier", Name=event)
        label_geom = ET.SubElement(label_block, "LabelGeometry", Anchor="NW")
        ET.SubElement(label_geom, "Point", X="38", Y="-36")
        spline_geom = ET.SubElement(edge, "SplineGeometry")
        ET.SubElement(spline_geom, "Point", X="380", Y="182")

    # Add edges for target S1 -> S0
    if target_s0:
        edge = ET.SubElement(edge_list, "Edge", Source="S1", Target="S0")
        label_block = ET.SubElement(edge, "LabelBlock")
        for event in target_s0:
            ET.SubElement(label_block, "SimpleIdentifier", Name=event)
        label_geom = ET.SubElement(label_block, "LabelGeometry", Anchor="NW")
        ET.SubElement(label_geom, "Point", X="-57", Y="13")
        spline_geom = ET.SubElement(edge, "SplineGeometry")
        ET.SubElement(spline_geom, "Point", X="315", Y="256")

    # Add self-loop for S0
    edge = ET.SubElement(edge_list, "Edge", Source="S0", Target="S0")
    label_block = ET.SubElement(edge, "LabelBlock")
    ET.SubElement(label_block, "SimpleIdentifier", Name="assignSev")

    guard_action_block = ET.SubElement(edge, "GuardActionBlock")
    guards = ET.SubElement(guard_action_block, "Guards")

    # Add BinaryExpression for value
    sender_expr = ET.SubElement(guards, "BinaryExpression", Operator="&")
# add address_xml to sender_expr
    sender_expr.append(address_xml)
    value_condition = ET.SubElement(sender_expr, "BinaryExpression", Operator="|")
    for value in [0, 1]:
        value_eq = ET.SubElement(value_condition, "BinaryExpression", Operator="==")
        unary_expr = ET.SubElement(value_eq, "UnaryExpression", Operator="'")
        ET.SubElement(unary_expr, "SimpleIdentifier", Name="value")
        ET.SubElement(value_eq, "IntConstant", Value=str(value))

    label_geom = ET.SubElement(guard_action_block, "LabelGeometry", Anchor="NW")
    ET.SubElement(label_geom, "Point", X="0", Y="20")

    return root


#############################################################################################################

# xml testing
address_list = list(sender_list.values())

assignMsg_efsm = generate_assignMsg_efsm(source_s0, target_s0)

ComponentList.append(assignMsg_efsm)
add_events_to_xml('assignSev')

#############################################################################################################


#print(VariableComponent['AddressVariables'])
#print(transfer_efsm_list)
print(FunctionVariablesTEMP)
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