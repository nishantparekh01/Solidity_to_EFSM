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
def add_nodes_to_xml(node):



for efsm in pre_supremica['Components']:
    #print(efsm)

    if 'edge_list' in pre_supremica['Components'][efsm]:

        n_transitions = len(pre_supremica['Components'][efsm]['edge_list'])

        if n_transitions == 1:
            pre_supremica['Components'][efsm]['edge_list']['t0']['source_index'] = 'S0'
            pre_supremica['Components'][efsm]['edge_list']['t0']['target_index'] = 'S0'
            # adding events only if the events list is empty
            if not pre_supremica['Components'][efsm]['edge_list']['t0']['events']:
                event_name = str(efsm + '1')
                pre_supremica['Components'][efsm]['edge_list']['t0']['event'] = event_name
                add_events_to_xml(event_name)
        else:
            for i in range(n_transitions):
                if i == 0:
                    pre_supremica['Components'][efsm]['edge_list'][f't{i}']['source_index'] = 'S0'
                    pre_supremica['Components'][efsm]['edge_list'][f't{i}']['target_index'] = 'S1'
                    # adding events only if the events list is empty
                    if not pre_supremica['Components'][efsm]['edge_list'][f't{i}']['events']:
                        event_name = str(efsm + '1')
                        pre_supremica['Components'][efsm]['edge_list'][f't{i}']['event'] = event_name
                        add_events_to_xml(event_name)

                elif i == n_transitions - 1:
                    pre_supremica['Components'][efsm]['edge_list'][f't{i}']['source_index'] = 'S' + str(i)
                    pre_supremica['Components'][efsm]['edge_list'][f't{i}']['target_index'] = 'S0'
                    # adding events only if the events list is empty
                    if not pre_supremica['Components'][efsm]['edge_list'][f't{i}']['events']:
                        event_name = str(efsm + 'X')
                        pre_supremica['Components'][efsm]['edge_list'][f't{i}']['event'] = event_name
                        add_events_to_xml(event_name)
                else:
                    pre_supremica['Components'][efsm]['edge_list'][f't{i}']['source_index'] = 'S' + str(i)
                    pre_supremica['Components'][efsm]['edge_list'][f't{i}']['target_index'] = 'S' + str(i+1)
                    # adding events only if the events list is empty
                    if not pre_supremica['Components'][efsm]['edge_list'][f't{i}']['events']:
                        event_name = str(efsm + str(i+1))
                        pre_supremica['Components'][efsm]['edge_list'][f't{i}']['event'] = event_name
                        add_events_to_xml(event_name)


# Adding all the events to pre_supremica
pre_supremica['Events']['EventDeclList'] = ET.tostring(EventDeclList, encoding='unicode', method='xml')

print(json.dumps(pre_supremica))
#print(pre_supremica)