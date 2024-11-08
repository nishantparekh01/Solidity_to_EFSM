import subprocess
import json
from solidity_ast_parser import *
from json_contract import *

sol_list = final_sol_list # final_sol_list is from json_contract.py

final_result = []
for n_id in range(len(sol_list)):
            print('ID PROCESSING: ', n_id)
            final_result = lookup_table[ntype(sol_list[n_id])](sol_list[n_id])
            # final_result.append(final_result)  # Store each result

