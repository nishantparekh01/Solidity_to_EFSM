# import json
# from solidity_ast_parser import *
# ############### Loading json file ###################################
#
# f = open(r'original_casino_blocking.json')
# #f = open(r'escrow_v2_json.json')
# #f = open(r'escrow_blocking.json')
# data = json.load(f)
# sol_list = data['nodes'][1]['nodes']
#
# #####################################################################
#
# for n_id in range(len(sol_list)):
#     print('ID PROCESSING: ', n_id)
#     final_result = lookup_table[ntype(sol_list[n_id])](sol_list[n_id])

# import subprocess
# import os
# import json
#
#
# ############### Function to compile the contract and generate AST JSON ###############
# def compile_contract_to_ast(contract_file):
#     # Generate the output JSON file name based on the contract file name
#     contract_name = os.path.splitext(os.path.basename(contract_file))[0]
#     output_json_file = f"{contract_name}_ast.json"
#
#     # Command to generate the AST in compact JSON format using solc
#     command = ["solc", "--ast-compact-json", contract_file]
#
#     # Run the command and capture the output
#     result = subprocess.run(command, capture_output=True, text=True)
#
#     if result.returncode != 0:
#         print(f"Error compiling contract: {result.stderr}")
#         return None
#
#     # Write the output to the JSON file (will create the file if it doesn't exist)
#     with open(output_json_file, 'w') as f:
#         f.write(result.stdout)
#
#     print(f"AST written to {output_json_file}")
#     return output_json_file  # Return the generated JSON file name
#
#
# ############### Function to clean the JSON file by removing the extra string ###############
# def clean_json_file(file_path):
#     with open(file_path, 'r') as f:
#         content = f.read()
#
#     # Locate the starting point of the JSON data
#     start_index = content.find('{')  # Find the first '{' to start the JSON
#     if start_index != -1:
#         json_content = content[start_index:]  # Remove anything before the first '{'
#
#         try:
#             # Parse the cleaned JSON content
#             json_data = json.loads(json_content)
#             return json_data
#         except json.JSONDecodeError as e:
#             print(f"Error parsing JSON: {e}")
#             return None
#     else:
#         print("No valid JSON content found.")
#         return None
#
#
# ############### Main logic ###################################
# # Replace this with your actual contract file path
# contract_file = r'smart_contracts/escrow_blocking.sol'
#
# # Compile the contract and generate the AST JSON file
# generated_json_file = compile_contract_to_ast(contract_file)
#
# # Proceed only if the AST JSON file was successfully generated
# if generated_json_file:
#     # Clean the generated JSON file to remove any extra strings
#     cleaned_json_data = clean_json_file(generated_json_file)
#
#     # Proceed if the JSON data was successfully cleaned and loaded
#     if cleaned_json_data:
#         # Extract the relevant nodes
#         sol_list = cleaned_json_data['nodes'][1]['nodes']
#
#         # Process the nodes as per your existing logic
#         for n_id in range(len(sol_list)):
#             print('ID PROCESSING: ', n_id)
#             final_result = lookup_table[ntype(sol_list[n_id])](sol_list[n_id])


import subprocess
import json
from solidity_ast_parser import *


# ############### Function to clean the JSON file by removing the extra string ###############

def clean_json_content(json_content):
    # Locate the starting point of the JSON data
    start_index = json_content.find('{')  # Find the first '{' to start the JSON
    if start_index != -1:
        json_content_cleaned = json_content[start_index:]  # Remove anything before the first '{'

        try:
            # Parse the cleaned JSON content
            json_data = json.loads(json_content_cleaned)
            return json_data
        except json.JSONDecodeError as e:
            print(f"Error parsing JSON: {e}")
            return None
    else:
        print("No valid JSON content found.")
        return None

############### Function to compile the contract and return AST JSON in memory ###############
def compile_contract_to_ast_in_memory(contract_file):
    # Command to generate the AST in compact JSON format using solc
    command = ["C:/Windows/solcfolder/solc", "--ast-compact-json", contract_file]

    # Run the command and capture the output in memory
    result = subprocess.run(command, capture_output=True, text=True)

    if result.returncode != 0:
        print(f"Error compiling contract: {result.stderr}")
        return None
    else:
        #print(f"AST JSON generated successfully", result.stdout)
        result_json  = result.stdout
        #print(result_json)
        #print("type of output is: ", type(result.stdout))
    return  result_json
    # The JSON output from the solc compiler is captured in result.stdout

    # try:
    #     json_data = json.loads(result_json)  # Directly parse the JSON output
    #     print(f"AST JSON data loaded successfully", json_data)
    #     return json_data
    # except json.JSONDecodeError as e:
    #     print(f"Error parsing JSON: {e}")
    #     return None


############### Main logic ###################################
def process_contract_in_memory(contract_file):
    # Compile the contract and get the AST JSON data in memory
    raw_json_data = compile_contract_to_ast_in_memory(contract_file)

    clean_json = clean_json_content(raw_json_data)

    # Proceed if the JSON data was successfully generated and loaded
    if clean_json:
        # Extract the relevant nodes
        sol_list = clean_json['nodes'][1]['nodes']

        # Collect the final results in a list
        final_result = []
        for n_id in range(len(sol_list)):
            print('ID PROCESSING: ', n_id)
            final_result = lookup_table[ntype(sol_list[n_id])](sol_list[n_id])
            #final_results.append(final_result)  # Store each result

        return final_result  # Return the list of final results
    return None


# Example usage
contract_file = r'smart_contracts/escrow_v2_blocking.sol'  # Replace with the path to your contract
try:
    final_result = process_contract_in_memory(contract_file)
except Exception as e:
    print(f"Error processing contract: {e}")

#print("Final Result: ", final_result)
# This final_results list can now be accessed by other parts of your application
#print("Final Results: ", final_results)
