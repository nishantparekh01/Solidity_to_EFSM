import json

from ast_restructure import *

# Now I need a way to add events to the transitions. So I add events, source and target nodes to the transitions.
# And also create a separate structure for storing variables.

pre_supremica = final_result

for efsm in pre_supremica['Components']:
    print(efsm)

    if 'edge_list' in pre_supremica['Components'][efsm]:

        n_transitions = len(pre_supremica['Components'][efsm]['edge_list'])

        if n_transitions == 1:
            pre_supremica['Components'][efsm]['edge_list']['t0']['source_index'] = 'S0'
            pre_supremica['Components'][efsm]['edge_list']['t0']['target_index'] = 'S0'
            if not pre_supremica['Components'][efsm]['edge_list']['t0']['events']:
                pre_supremica['Components'][efsm]['edge_list']['t0']['event'] = str(efsm + '1')
        else:
            for i in range(n_transitions):
                if i == 0:
                    pre_supremica['Components'][efsm]['edge_list'][f't{i}']['source_index'] = 'S0'
                    pre_supremica['Components'][efsm]['edge_list'][f't{i}']['target_index'] = 'S1'
                    # add events only if the events list is empty
                    if pre_supremica['Components'][efsm]['edge_list'][f't{i}']['events'] == '':
                        pre_supremica['Components'][efsm]['edge_list'][f't{i}']['event'] = str(efsm + '1')
                elif i == n_transitions - 1:
                    pre_supremica['Components'][efsm]['edge_list'][f't{i}']['source_index'] = 'S' + str(i)
                    pre_supremica['Components'][efsm]['edge_list'][f't{i}']['target_index'] = 'S0'
                    if pre_supremica['Components'][efsm]['edge_list'][f't{i}']['events'] == '':
                        pre_supremica['Components'][efsm]['edge_list'][f't{i}']['event'] = str(efsm + 'X')
                else:
                    pre_supremica['Components'][efsm]['edge_list'][f't{i}']['source_index'] = 'S' + str(i)
                    pre_supremica['Components'][efsm]['edge_list'][f't{i}']['target_index'] = 'S' + str(i+1)
                    if pre_supremica['Components'][efsm]['edge_list'][f't{i}']['events'] == '':
                        pre_supremica['Components'][efsm]['edge_list'][f't{i}']['event'] = str(efsm + str(i+1))


    print(json.dumps(pre_supremica))
    print(pre_supremica)