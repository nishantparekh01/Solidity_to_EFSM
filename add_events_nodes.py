import json

from ast_restructure import *

# Now I need a way to add events to the transitions. So I add events, source and target nodes to the transitions.
# And also create a separate structure for storing variables.

pre_supremica = final_result

# Creating the EventDecl xml here
EventDeclList = ET.Element("EventDeclList")

# Create a separate eventdecl for this
# <EventDecl Kind="PROPOSITION" Name=":accepting"/>

# Need to write a function for adding generated events to xml eventdecl
def add_events_to_xml(event): # event is a string
    global EventDeclList
    EventDecl = ET.SubElement(EventDeclList, "EventDecl",Kind = "CONTROLLABLE", Name = event)
    #EventDeclList.append(EventDecl)


# A function to add nodes to node_list
def add_nodes_to_xml(node_list):
    # Exameple of node_list = ['S0', 'S1', 'S2', 'S3']
    NodeList = ET.Element("NodeList")
    for node in node_list:
        if node == 'S0':
            SimpleNode = ET.SubElement(NodeList, "SimpleNode", Initial = "true",  Name = node)
            EventList = ET.SubElement(SimpleNode, "EventList")
            SimpleIdentifier_accepting = ET.SubElement(EventList, "SimpleIdentifier", Name = ":accepting")
        else:
            SimpleNode = ET.SubElement(NodeList, "SimpleNode",  Name = node)

    return  NodeList


# Creating a list to add all the nodes for a specific efsm
#efsm_node_list = []

def add_node_to_efsm_node_list(source_node, target_node):
    if source_node not in efsm_node_list:
        efsm_node_list.append(source_node)

    if target_node not in efsm_node_list:
        efsm_node_list.append(target_node)



for efsm in pre_supremica['Components']:
    #print(efsm)
    #global efsm_node_list
    efsm_node_list = []

    if 'edge_list' in pre_supremica['Components'][efsm]:

        n_transitions = len(pre_supremica['Components'][efsm]['edge_list'])

        if n_transitions == 1:
            source_node = 'S0'
            target_node = source_node
            pre_supremica['Components'][efsm]['edge_list']['t0']['source_index'] = source_node
            pre_supremica['Components'][efsm]['edge_list']['t0']['target_index'] = target_node
            add_node_to_efsm_node_list(source_node, target_node)

            # adding events only if the events list is empty
            if not pre_supremica['Components'][efsm]['edge_list']['t0']['events']:
                event_name = str(efsm + '1')
                pre_supremica['Components'][efsm]['edge_list']['t0']['event'] = event_name
                add_events_to_xml(event_name)
        else:
            for i in range(n_transitions):
                if i == 0:
                    source_node = 'S0'
                    target_node = 'S1'
                    pre_supremica['Components'][efsm]['edge_list'][f't{i}']['source_index'] = source_node
                    pre_supremica['Components'][efsm]['edge_list'][f't{i}']['target_index'] = target_node
                    add_node_to_efsm_node_list(source_node, target_node)

                    # adding events only if the events list is empty
                    if not pre_supremica['Components'][efsm]['edge_list'][f't{i}']['events']:
                        event_name = str(efsm + '1')
                        pre_supremica['Components'][efsm]['edge_list'][f't{i}']['event'] = event_name
                        add_events_to_xml(event_name)

                elif i == n_transitions - 1:
                    source_node = 'S' + str(i)
                    target_node = 'S0'
                    pre_supremica['Components'][efsm]['edge_list'][f't{i}']['source_index'] = source_node
                    pre_supremica['Components'][efsm]['edge_list'][f't{i}']['target_index'] = target_node
                    add_node_to_efsm_node_list(source_node, target_node)

                    # adding events only if the events list is empty
                    if not pre_supremica['Components'][efsm]['edge_list'][f't{i}']['events']:
                        event_name = str(efsm + 'X')
                        pre_supremica['Components'][efsm]['edge_list'][f't{i}']['event'] = event_name
                        add_events_to_xml(event_name)
                else:
                    source_node = 'S' + str(i)
                    target_node = 'S' + str(i+1)
                    pre_supremica['Components'][efsm]['edge_list'][f't{i}']['source_index'] = source_node
                    pre_supremica['Components'][efsm]['edge_list'][f't{i}']['target_index'] = target_node
                    add_node_to_efsm_node_list(source_node, target_node)

                    # adding events only if the events list is empty
                    if not pre_supremica['Components'][efsm]['edge_list'][f't{i}']['events']:
                        event_name = str(efsm + str(i+1))
                        pre_supremica['Components'][efsm]['edge_list'][f't{i}']['event'] = event_name
                        add_events_to_xml(event_name)

    # Adding the node_list to pre_supremica
    nodes_xml = add_nodes_to_xml(efsm_node_list)
    pre_supremica['Components'][efsm]['node_list'] = ET.tostring(nodes_xml, encoding='unicode', method='xml')


# Adding all the events to pre_supremica
pre_supremica['Events']['EventDeclList'] = ET.tostring(EventDeclList, encoding='unicode', method='xml')

print(json.dumps(pre_supremica))
#print(pre_supremica)