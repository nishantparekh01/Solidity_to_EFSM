import subprocess
import json

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


############### Main logic ###################################
def process_contract_in_memory(contract_file):
    # Compile the contract and get the AST JSON data in memory
    raw_json_data = compile_contract_to_ast_in_memory(contract_file)

    clean_json = clean_json_content(raw_json_data)

    # Proceed if the JSON data was successfully generated and loaded
    if clean_json:
        # Extract the relevant nodes
        print(json.dumps(clean_json))
        sol_list = clean_json['nodes'][1]['nodes']

        # # Collect the final results in a list
        # final_result = []
        # for n_id in range(len(sol_list)):
        #     print('ID PROCESSING: ', n_id)
        #     final_result = lookup_table[ntype(sol_list[n_id])](sol_list[n_id])
        #     #final_results.append(final_result)  # Store each result

        return sol_list  # Return the list of final results
    return None

final_sol_list = []
# Example usage
contract_file = r'smart_contracts/casino_nonblocking.sol'  # Replace with the path to your contract
try:
    final_sol_list = process_contract_in_memory(contract_file)
except Exception as e:
    print(f"Error processing contract: {e}")

print(len(final_sol_list))