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
def add_events_to_xml(event):  # event is a string
    global EventDeclList
    EventDecl = ET.SubElement(EventDeclList, "EventDecl", Kind="CONTROLLABLE", Name=event)


# Creating a list to add all the nodes for a specific efsm
def add_node_to_efsm_node_list(source_node, target_node):
    if source_node not in efsm_node_list:
        efsm_node_list.append(source_node)

    if target_node not in efsm_node_list:
        efsm_node_list.append(target_node)


for efsm in pre_supremica['Components']:
    efsm_node_list = []
    if efsm != 'VariableComponent':
        if 'edge_list' in pre_supremica['Components'][efsm]:

            n_transitions = len(pre_supremica['Components'][efsm]['edge_list'])
            EdgeList = ET.Element("EdgeList")

            for i in range(n_transitions):
                processing_transition = pre_supremica['Components'][efsm]['edge_list'][f't{i}']

                if i == 0:
                    source_node = 'S0'
                else:
                    source_node = 'S' + str(i)

                if processing_transition['transition_type'] == 'self_loop':
                    # Handling self-loop, source and target nodes are the same
                    target_node = source_node
                else:
                    target_node = 'S' + str(i + 1)

                processing_transition['source_index'] = source_node
                processing_transition['target_index'] = target_node
                add_node_to_efsm_node_list(source_node, target_node)

                # Adding events only if the events list is empty
                if not processing_transition['events']:
                    event_name = str(efsm + str(i + 1))
                    pre_supremica['Components'][efsm]['edge_list'][f't{i}']['event'] = event_name
                    add_events_to_xml(event_name)

                transition_xml = add_transition_to_xml(processing_transition)
                EdgeList.append(transition_xml)

            pre_supremica['Components'][efsm]['edge_list'] = EdgeList

        # Adding the node_list to pre_supremica
        nodes_xml = add_nodes_to_xml(efsm_node_list)
        pre_supremica['Components'][efsm]['node_list'] = nodes_xml

# Adding all the events to pre_supremica
pre_supremica['Events'] = EventDeclList
