import json
from solidity_ast_parser import *
############### Loading json file ###################################
f = open(r'original_casino_blocking.json')
data = json.load(f)
sol_list = data['nodes'][1]['nodes']
#####################################################################


######################## CHECK - ModifierDefinition ##############
# ModifierDefinition nodes : 11, 12, 13
# Status : Checked
# Output type -> "Enum_variable_name : [ list of member names ]"

# ModifierDefinition_node_list = [11,12,13]
# for n_id in ModifierDefinition_node_list:
#     result = lookup_table[ntype(sol_list[n_id])](sol_list[n_id])
#     json_result = json.dumps(result)
#     print(json_result)
#     #print(lookup_table[ntype(sol_list[n_id])](sol_list[n_id]))
#     print("\n")
#     print("-------------")
#     print("\n")


######################## CHECK - FunctionDefinition ##############
# FunctionDefinition nodes : 14 to 24
# Status : Checked
# Output type -> Function definition as in code.

# FunctionDefinition_node_list = [i for i in range(14,25)]
#
# for n_id in FunctionDefinition_node_list:
#     result = lookup_table[ntype(sol_list[n_id])](sol_list[n_id])
#     json_result = json.dumps(result)
#     print(json_result)
#     # print(lookup_table[ntype(sol_list[n_id])](sol_list[n_id]))
#     print("\n")
#     print("-------------")
#     print("\n")

######################## CHECK - 11-24 ##############
# FunctionDefinition nodes : 14 to 24
# Status : Checked
# Output type -> Function definition as in code.

Fun_node_list = [11,12,13,15,16,17,18,19,21,22,23,24,20]
original_casino_blocking_list = [2,3,4,5,6,7,8,9,10, 12, 13, 14, 15, 16, 17,18, 19, 20, 21, 22]

#final_result = json.dumps({})

for n_id in original_casino_blocking_list:
    print('ID PROCESSING: ', n_id)
    final_result = lookup_table[ntype(sol_list[n_id])](sol_list[n_id])
    #json_result = result
    #final_result = json_result
    #print(n_id)
    #print(json_result)
    # print(lookup_table[ntype(sol_list[n_id])](sol_list[n_id]))
    # print("\n")
    # print("-------------")
    # print("\n")
print(type((final_result)))
#print(json.dumps(final_result))