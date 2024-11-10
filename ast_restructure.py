import json

from test_supremica_generator import *

# pre_supremica = json.loads(final_result)
pre_supremica = final_result


def check_action_present(transition):
    if transition['action_exp'] != None:
        return True
    else:
        return


def get_ntype_eval_exp(transition):
    if transition['evaluate_exp'] != None and transition['evaluate_exp'] != False:
        return transition['evaluate_exp']['ntype']
    else:
        return None


def restructure(pre_supremica):
    processing_node = {}

    for efsm in pre_supremica['Components']:
        processing_node = {}
        processing_transition = {}
        if efsm != 'VariableComponent':
            for i in range(len(pre_supremica['Components'][efsm]['edge_list'])):
                processing_transition = pre_supremica['Components'][efsm]['edge_list'][f't{i}']
                if i != 0:
                    previous_transition = pre_supremica['Components'][efsm]['edge_list'][f't{i - 1}']

                if processing_transition['transition_type'] == 'false_body_absent' or processing_transition['transition_type'] == 'false_body_last':
                    continue

                if processing_transition['action_exp'] == None:
                    # check ntype of evaluate_expression
                    if get_ntype_eval_exp(processing_transition) == 'VariableDeclarationStatement':   #or processing_transition['transition_type'] == 'false_body_absent' or processing_transition['transition_type'] == 'false_body_last':
                        break

                    if not check_action_present(processing_transition): # isn't this the same as the above if statement?
                        processing_node = processing_transition
                else:
                    if processing_node != {}: # I don't understand this condition and what it does
                        processing_node['action_exp'] = processing_transition['action_exp']
                        processing_transition['evaluate_exp'] = False
                        processing_transition['action_exp'] = None
                        processing_node = {}


# create a function that handles conditional and if statements


# create a function that will track the nodes created and add them to the node_list


# Function to remove transitions with evaluate_exp as False
def check_false_evaluate(transition, efsm, transition_name):
    if transition['evaluate_exp'] == False:
        # remove that node from the pre_supremica
        # remove pre_supremica['Components']['#efsm_name']['edge_list'][#transition_number']
        # print(f'Removing transition {efsm}[ {transition_name} ]' )
        del pre_supremica['Components'][efsm]['edge_list'][transition_name]
        return True  # return true if transition is removed


# final for loop run

# calling the function to restructure the pre_supremica
restructure(pre_supremica)

# removing transitions with evaluate_exp as False
for efsm in pre_supremica['Components']:
    if efsm != 'VariableComponent':
        for transition in list(pre_supremica['Components'][efsm]['edge_list']):
            check_false_evaluate(pre_supremica['Components'][efsm]['edge_list'][transition], efsm, f'{transition}')
            # print(transition)

# reorder transition names after deleting some
for efsm in pre_supremica['Components']:
    if efsm != 'VariableComponent':
        for i, transition in enumerate(list(pre_supremica['Components'][efsm]['edge_list'])):
            pre_supremica['Components'][efsm]['edge_list'][f't{i}'] = pre_supremica['Components'][efsm][
                'edge_list'].pop(transition)

# remove 'evaluate_exp' from the transitions
for efsm in pre_supremica['Components']:
    if efsm != 'VariableComponent':
        for transition in pre_supremica['Components'][efsm]['edge_list']:
            pre_supremica['Components'][efsm]['edge_list'][transition].pop('evaluate_exp')

final_result = pre_supremica
# print(type(pre_supremica))
