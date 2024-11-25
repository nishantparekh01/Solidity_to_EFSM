# efsm = { # This represents one entire EFSM
#     'name': name, # name of the efsm
#     'transitions' : [ # list of transitions present in this EFSM
#         {'source_node': 'q0',
#          'target_node': next_node,
#          'event': event,
#          'guard': guard,
#          'action': action},
#         {
#
#         }
#     ]
#
# }
import xml.etree.ElementTree as ET
from wmodify import *
from copy import deepcopy
from json_contract import *  # load the list of nodes from the json_contract.py file corresponding to the contract

Supremica = {}

modifier_objects_dict = {}

# Events - contains list of all events
Supremica['Events'] = {}
Events = Supremica['Events']

# Components - contains all efsms
Supremica['Components'] = {}
Components = Supremica['Components']

# Variable Component - Contains all variables
Components['VariableComponent'] = {}
VariableComponent = Components['VariableComponent']
VariableComponent['EnumVariables'] = {}
VariableComponent['StructVariables'] = {}

# creating a dictionary to store all generated addresses
VariableComponent['AddressVariables'] = {}

# creating a dictionary to store all generated boolean variables
VariableComponent['BooleanVariables'] = {}

# creating a dictionary to store Mapping variables
VariableComponent['MappingVariables'] = {}

# declaring address_index to keep track of address variables
address_index = 0

# Initial Node = S0
INITIAL_NODE = 'S0'

# list for transfer efsms
transfer_efsm_list = []


class EFSM:
    def __init__(self,
                 name):  # This is to create the structure for each efsm. Right for modifiers. Later for all functions
        self.params_dict = {}
        #self.guard_transition_template = []
        self.name = name
        self.efsm = {}

        self.efsm['node_list'] = {}
        self.node_list = self.efsm['node_list']

        self.efsm['edge_list'] = {}
        self.edge_list = self.efsm['edge_list']
        self.i = 0

    def addTransition(self, expression):

        transition_type = str()
        source_index = None
        target_index = None
        events = []
        guard_exp = None
        action_exp = None
        evaluate_exp = None
        evaluate_exp = expression  # This should be derived if 'FunctionCall' is require.

        # we have to check the ntype of expression and then add the transition accordingly
        # we should check this by creating a function call and then checking the ntype of the expression
        if expression:  # This is for the placeholder statement


            if expression['ntype'] == 'FunctionCall':
                if expression['name'] == 'require':
                    # assuming that require has only one argument
                    guard_exp = expression['args']
                    transition_type = 'require_true'
                    # guard_exp = ET.tostring(expression['args'], encoding='unicode', method='xml')
                # elif expression['name'] == 'keccak256':
                elif 'type' in expression and expression['type'] == 'transfer':
                    transition_type = 'self_loop'
                    events.append(str(expression['name'] + '1'))
                    # transfer_success = {'ntype': 'Simple', 'name': 'transfer_success', 'args': 'true'}
                    # transfer_failure = {'ntype': 'Simple', 'name': 'transfer_failure', 'args': 'false'}

                else:

                    # action_exp = str(expression['name'] + '(' + expression['args'] + ')')
                    transition_type = 'self_loop'
                    events.append(str(expression['name'] + '1'))

            elif expression['ntype'] == 'Simple':
                if 'name' in expression:
                    events.append(expression['name'])
                    if expression['type'] == 'efsm_fail':
                        transition_type = 'efsm_fail'
                        target_index = INITIAL_NODE

                    elif expression['type'] == 'transfer_success':
                        transition_type = 'transfer_success'

                    elif expression['type'] == 'transfer_fail':
                        transition_type = 'transfer_fail'

                    elif expression['type'] == 'transfer_efsm_fail':
                        target_index = INITIAL_NODE

                    elif expression['type'] == 'true_body_last' or expression['type'] == 'false_body_last':
                        transition_type = expression['type']

                    elif expression['type'] == 'function_fail':
                        target_index = INITIAL_NODE

                    elif expression['type'] == 'modifier_guard':
                        transition_type = 'self_loop'
                        guard_exp = expression['guard_exp']

                    elif expression['type'] == 'sender_transfer_initial':
                        transition_type = 'sender_transfer_initial'

                    elif expression['type'] == 'sender_transfer':
                        transition_type = 'sender_transfer'

                    elif expression['type'] == 'sender_transfer_success_initial':
                        transition_type = 'sender_transfer_success_initial'

                    elif expression['type'] == 'sender_transfer_success':
                        transition_type = 'sender_transfer_success'

                    elif expression['type'] == 'require_false':
                        guard_exp = expression['guard_exp']
                        transition_type = expression['type']

                elif 'type' in expression and expression['type'] == 'param_assignment':
                    guard_exp = expression['guard_exp']
                    transition_type = expression['type']

                # elif 'type' in expression and expression['type'] == 'require_false':
                #     guard_exp = expression['guard_exp']
                #     transition_type  = expression['type']






            elif expression['ntype'] == 'Assignment':
                if expression['kind'] == 'conditional':
                    guard_exp = expression['expression']
                    # true_body = expression['lhs'] + ' = ' + expression['true_exp']
                    # false_body = expression['lhs'] + ' = ' + expression['false_exp']
                    # true_expression_dict = {'ntype': 'Assignment', 'kind': 'simple', 'exp': true_body}
                    # false_expression_dict = {'ntype': 'Assignment', 'kind': 'simple', 'exp': false_body}

                    # self.addTransition(true_expression_dict)
                    # self.addTransition(false_expression_dict)
                elif expression['kind'] == 'simple':
                    # if expression['exp'] != None:
                    #     action_exp = expression['exp']
                    # else:
                    #     action_exp = None
                    action_exp = expression['exp']

                elif expression['kind'] == 'mapping_assignment_check':
                    #print('Mapping Assignment Check')
                    guard_exp = expression['expression']

                if 'type' in expression:
                    transition_type = expression['type']
                    # action_exp = ET.tostring(expression['exp'], encoding='unicode', method='xml')


            elif expression['ntype'] == 'VariableDeclarationStatement':
                if expression['kind'] == 'conditional':
                    # condition = expression['condition']
                    # true_body = expression['name'] + ' == ' + expression['true_exp']
                    # false_body = expression['name'] + ' == ' + expression['false_exp']
                    # guard_exp = str("(" + condition + " & " + true_body + ") | (" + "!" + "(" + condition + ")" + " & " + false_body + ")")
                    guard_exp = expression['expression']
                    # guard_exp = ET.tostring(expression['expression'], encoding='unicode', method='xml')

                elif expression['kind'] == 'mapping_assignment_check':
                    #print('Mapping Assignment Check')
                    guard_exp = expression['expression']
                    #print(asdf)


            elif expression['ntype'] == 'IfStatement':

                if 'kind' in expression and expression['kind'] == 'internal':
                    if expression['condition'] == 'true':
                        guard_exp = expression['guard_exp']
                        transition_type = expression['type']
                #         # guard_exp = ET.tostring(expression['guard_exp'], encoding='unicode', method='xml')
                #         # action_exp = expression['exp']  # Assumption: only one expression in the body
                    elif expression['condition'] == 'false':
                        guard_exp = expression['guard_exp']
                        transition_type = expression['type']
                #         # guard_exp = ET.tostring(expression['guard_exp'], encoding='unicode', method='xml')
                #         # action_exp = expression['exp'] # Assumption: only one expression in the body



        transition = {
            'transition_type': transition_type,
            'source_index': source_index,
            'target_index': target_index,
            'events': events,
            'guard_exp': guard_exp,
            'action_exp': action_exp,
            'evaluate_exp': evaluate_exp
        }

        self.edge_list[f't{self.i}'] = transition
        self.i += 1

    def addModifierInvocation(self, modifiers):
        # Assumption that modifier right now has only one statement, which is the require statement.
        # issue #1 in nishantparekh01/casino_conversion
        for m in modifiers:
            # if m in Components:
            # m['name'] is the name of the modifier

            mod = m['name']

            if 'args' in m:
                mod = modifier_objects_dict[mod]
                event_name = self.name + '1'
                params_dict_key_list = list(mod.params_dict.keys())
                for i, param_value in enumerate(m['args']):
                    mod.params_dict[params_dict_key_list[i]] = param_value
                #print(mod.guard_transition_template[0]) # Why 0 here ? Refer to issue #39 in nishantparekh01/casino_conversion/test1

                replacement_guard = mod.guard_transition_template[0]
                if 'args' in replacement_guard:
                    root = deepcopy(replacement_guard['args'])
                    for si in root.findall('.//SimpleIdentifier'):    # This is to replace the name of the variables in the guard expression with the values passed in the modifier
                        current_name = si.get('Name')
                        if current_name in mod.params_dict:
                            si.set('Name', mod.params_dict[current_name])

                guard_transition = {'ntype': 'Simple', 'name': event_name, 'type': 'modifier_guard', 'guard_exp': root}

                mod.addTransition(guard_transition)

            else:
                Components[mod]['edge_list']['t0']['events'].append(self.name + '1')

    def addModifierParameter(self, parameters):

        for p in parameters:
            self.params_dict[p] = str()

    def add_transfer(self, expression):
        transition_type = 'self_loop'
        events = []
        guard_exp = None
        action_exp = None
        evaluate_exp = None
        evaluate_exp = expression


def superEnumDefinition(packet):
    global VariableComponent
    name = packet['name']
    members = packet['members']

    VariableComponent['EnumVariables'][name] = members
    return True


def superStructDefinition(packet):
    global VariableComponent
    name = packet['name']
    members = packet['members']

    VariableComponent['StructVariables'][name] = members
    return True


def get_address_index():
    global address_index
    address_index += 1
    return address_index


def superVariableDeclaration(packet):
    global VariableComponent
    name = packet['name']
    type = packet['type']

    if type in VariableComponent['EnumVariables']:
        members = VariableComponent['EnumVariables'][type]

        xml_VariableComponent = ET.Element("VariableComponent", Name=name)
        xml_variableRange = ET.SubElement(xml_VariableComponent, "VariableRange")
        xml_EnumSetExpression = ET.SubElement(xml_variableRange, "EnumSetExpression")
        for mem in members:
            ET.SubElement(xml_EnumSetExpression, "SimpleIdentifier", Name=mem)

        xml_VariableInitial = ET.SubElement(xml_VariableComponent, "VariableInitial")
        xml_initialValue = wmodify_assignment(name, "==", members[0])
        xml_VariableInitial.append(xml_initialValue)
        VariableComponent[name] = xml_VariableComponent
        # VariableComponent[name] = ET.tostring(xml_VariableComponent, encoding='unicode', method='xml')
        # str_xml_VariableComponent = ET.tostring(xml_VariableComponent, encoding='unicode', method='xml')
        # VariableComponent.append(str_xml_VariableComponent)

    elif type == 'uint' or type == 'uint256' or type == 'bytes32':

        xml_VariableComponent = ET.Element("VariableComponent", Name=name)
        xml_variableRange = ET.SubElement(xml_VariableComponent, "VariableRange")
        xml_NumericRangeExpression = wmodify_assignment("0", "..", "1")
        xml_variableRange.append(xml_NumericRangeExpression)

        xml_VariableInitial = ET.SubElement(xml_VariableComponent, "VariableInitial")
        xml_initialValue = wmodify_assignment(name, "==", "0")
        xml_VariableInitial.append(xml_initialValue)
        VariableComponent[name] = xml_VariableComponent
        # VariableComponent[name] = ET.tostring(xml_VariableComponent, encoding='unicode', method='xml')
        # str_xml_VariableComponent = ET.tostring(xml_VariableComponent, encoding='unicode', method='xml')
        # VariableComponent.append(str_xml_VariableComponent)

    elif type == 'address':

        # name has the name and type has value 'address'
        # set address index to 0 and increment it for each address
        # append the address index to the address name

        address_index = get_address_index()
        address_name = 'x000' + str(address_index)

        # Add this to the dictionary AddressVariables
        VariableComponent['AddressVariables'][name] = address_name

        # create the xml element for the address
        xml_VariableComponent = ET.Element("VariableComponent", Name=name)
        xml_variableRange = ET.SubElement(xml_VariableComponent, "VariableRange")
        xml_EnumSetExpression = ET.SubElement(xml_variableRange, "EnumSetExpression")

        ET.SubElement(xml_EnumSetExpression, "SimpleIdentifier", Name=address_name)

        xml_VariableInitial = ET.SubElement(xml_VariableComponent, "VariableInitial")
        xml_initialValue = wmodify_assignment(name, "==", address_name)
        xml_VariableInitial.append(xml_initialValue)
        VariableComponent[name] = xml_VariableComponent

    elif type == 'Mapping':
        #print(packet)
        #{'name': 'withdrawable', 'type': 'Mapping', 'key_value': 'address_uint'}
        mapping_name = packet['name']
        mapping_key_value  = packet['key_value']
        if mapping_key_value == 'address_uint':
            AddressVariables = VariableComponent['AddressVariables']
            # generate variable names combining address and mapping name

            # Store the generated mapping variables in the dictionary MappingVariables with mapping variable name as the key
            VariableComponent['MappingVariables'][mapping_name] = {}
            for declared_address in AddressVariables.keys():
                #print(mapping_name + '_'+ declared_address)
                mapping_variable = mapping_name + '_'+ declared_address
                VariableComponent['MappingVariables'][mapping_name][declared_address] = mapping_variable
                #print(VariableComponent['MappingVariables'])


        #gyg = gyg - 2
    elif type == 'bool':
        members =['false', 'true']

        xml_VariableComponent = ET.Element("VariableComponent", Name=name)
        xml_variableRange = ET.SubElement(xml_VariableComponent, "VariableRange")
        xml_EnumSetExpression = ET.SubElement(xml_variableRange, "EnumSetExpression")
        for mem in members:
            ET.SubElement(xml_EnumSetExpression, "SimpleIdentifier", Name=mem)

        xml_VariableInitial = ET.SubElement(xml_VariableComponent, "VariableInitial")
        xml_initialValue = wmodify_assignment(name, "==", members[0])
        xml_VariableInitial.append(xml_initialValue)
        VariableComponent[name] = xml_VariableComponent
        #print('bool variable added', name)

        # Add this to the dictionary AddressVariables
        VariableComponent['BooleanVariables'][name] = members
        #print('Boolean Variables: ', VariableComponent['BooleanVariables'])

def addAutomata(efsm):
    global Components
    Components[efsm.name] = efsm.efsm


def superModifierDefinition(packet):
    # must return a dictionary
    global Supremica

    name = packet['name']  # name of modifier
    # fill the name here. Create a new efsm
    # To create the ast, for each level we need a function

    params = packet['params']
    # Use parameters in whichever way
    body = packet['body']  # list of expressions
    # Generate transitions using expressions here.

    # Create modifier object
    modifier = EFSM(name)

    if params:
        modifier.addModifierParameter(params)
        modifier.guard_transition_template = body
    else:
        for exp in body:
            #modifier.addTransition(exp)
            print(exp)
            if exp != False:
             process_in_ignore_list(exp, 'args', ignore_list, modifier)



    # Add modifier to the global dictionary
    modifier_objects_dict[name] = modifier

    addAutomata(modifier)
    return Supremica

def add_transfer_efsm(efsm_name):
    #efsm_name = efsm_name
    #print('ADding efsm-----------', efsm_name)
    transfer_efsm_name = efsm_name  # operatortransfer
    if  transfer_efsm_name not in transfer_efsm_list:


        transfer_efsm = EFSM(transfer_efsm_name)
        transfer_efsm_list.append(transfer_efsm_name)
        # transfer_efsm.add_transfer(exp)

        # transition for transfer event
        #transfer_event = {'ntype': 'Simple', 'name': efsm_name + 'transfer' + '1', 'type': 'transfer_event'}
        transfer_event = {'ntype': 'Simple', 'name': efsm_name  + '1', 'type': 'transfer_event'}
        transfer_efsm.addTransition(transfer_event)

        # transition for transfer fail
        #transfer_fail = {'ntype': 'Simple', 'name': efsm_name + 'transfer' + 'Fail', 'type': 'transfer_efsm_fail'}
        transfer_fail = {'ntype': 'Simple', 'name': efsm_name + 'Fail', 'type': 'transfer_efsm_fail'}
        transfer_efsm.addTransition(transfer_fail)

        # transition for transfer success
        #transfer_success = {'ntype': 'Simple', 'name': efsm_name + 'transfer' + 'X', 'type': 'transfer_efsm_success'}
        transfer_success = {'ntype': 'Simple', 'name': efsm_name + 'X', 'type': 'transfer_efsm_success'}
        transfer_efsm.addTransition(transfer_success)

        addAutomata(transfer_efsm)


def check_require_in_function(body):
    for exp in body:
        if 'ntype' in exp and exp['ntype'] == 'FunctionCall':
            if exp['name'] == 'require':
                return True
    return False


def check_parameter_in_require( body, search_string):
    # check for all parameter if they are present in any require statement
    # Check if the search string is in the element's text
    for exp in body:
        if 'ntype' in exp and exp['ntype'] == 'FunctionCall':
            if exp['name'] == 'require':
                element = exp['args']

                if element.text and search_string in element.text:
                    return True

                # Check if the search string is in the element's tail text
                if element.tail and search_string in element.tail:
                    return True

                # Check if the search string is in any of the element's attributes
                for attribute in element.attrib.values():
                    if search_string in attribute:
                        return True

                # Recursively check all child elements
                for child in element:
                    if in_ignore_list(child, search_string):
                        return True

                # If none of the conditions are met
                return False

        return False




def superFunctionDefinition(packet):
    global false_body
    name = packet['name']
    params = packet['params']
    print('params', params)
    global param_assigned
    param_assigned = False
    body = packet['body']
    modifiers = packet['modifiers']
    global initial_statement_added
    initial_statement_added = False


    # Create EFSM instance of function
    function = EFSM(name)

    require_in_function = check_require_in_function(body)
    if require_in_function:
        print('Require in function', name)

        for param, param_type in params.items():
            # check if the parameter is present in the require statement
            if check_parameter_in_require(body, param):
                # Add parameter to the function
                print('Parameter present in require statement', param, param_type)

                if param_type in VariableComponent['EnumVariables']:
                    # generate xml expression where param = param_type[0] | param_type[1] | param_type[2] | ...
                    guard_exp = wmodify_assignment(param, "==", VariableComponent['EnumVariables'][param_type],
                                                   **{'ntype': 'ParameterDeclarationStatement',
                                                      'kind': 'AssignmentCheck'})
                    # print(ET.tostring(guard_exp, encoding='unicode', method='xml'))
                    param_assignment = {'ntype': 'Simple', 'guard_exp': guard_exp, 'type': 'param_assignment'}
                    function.addTransition(param_assignment)
                    param_assigned = True
                    initial_statement_added = True

                elif param_type == 'uint' or param_type == 'uint256' or param_type == 'bytes32':
                    rhs_list = ['0', '1']
                    guard_exp = wmodify_assignment(param, "==", rhs_list, **{'ntype': 'ParameterDeclarationStatement',
                                                                             'kind': 'AssignmentCheck'})
                    param_assignment = {'ntype': 'Simple', 'guard_exp': guard_exp, 'type': 'param_assignment'}
                    function.addTransition(param_assignment)
                    param_assigned = True
                    initial_statement_added = True
    else:
        # add parameters to the function
        for param, param_type in params.items():
            # print(param, param_type, 'param and param_type')
            if param_type in VariableComponent['EnumVariables']:
                # generate xml expression where param = param_type[0] | param_type[1] | param_type[2] | ...
                guard_exp = wmodify_assignment(param, "==", VariableComponent['EnumVariables'][param_type],
                                               **{'ntype': 'ParameterDeclarationStatement',
                                                  'kind': 'AssignmentCheck'})
                # print(ET.tostring(guard_exp, encoding='unicode', method='xml'))
                param_assignment = {'ntype': 'Simple', 'guard_exp': guard_exp, 'type': 'param_assignment'}
                function.addTransition(param_assignment)
                param_assigned = True

            elif param_type == 'uint' or param_type == 'uint256' or param_type == 'bytes32':
                rhs_list  = ['0','1']
                guard_exp = wmodify_assignment(param, "==", rhs_list, **{'ntype': 'ParameterDeclarationStatement',
                                                                  'kind': 'AssignmentCheck'})
                param_assignment = {'ntype': 'Simple', 'guard_exp': guard_exp, 'type': 'param_assignment'}
                function.addTransition(param_assignment)
                param_assigned = True

    # Add function name to invoked modifiers
    if modifiers:
        function.addModifierInvocation(modifiers)

    # Add transitions to the function based on parameters and its respective values

    for exp_index, exp in enumerate(body):
        #print(exp_index)
        if 'type' in exp and exp['type'] == 'transfer':
            transfer_in_function_name = str()

            if exp_index == 0:
                first_transition = {'ntype': 'Simple', 'name': name + '1', 'type': 'first_transition'}
                function.addTransition(first_transition)
                transfer_in_function_name = name + exp['name']
                add_transfer_efsm(transfer_in_function_name)
                # if exp['name'] not in transfer_efsm_list:
                #     transfer_efsm = EFSM(exp['name'])
                #     transfer_efsm_list.append(exp['name'])
                #     # transfer_efsm.add_transfer(exp)
                #
                #     # transition for transfer event
                #     transfer_event = {'ntype': 'Simple', 'name': exp['name'] + '1', 'type': 'transfer_event'}
                #     transfer_efsm.addTransition(transfer_event)
                #
                #     # transition for transfer fail
                #     transfer_fail = {'ntype': 'Simple', 'name': exp['name'] + 'Fail', 'type': 'transfer_efsm_fail'}
                #     transfer_efsm.addTransition(transfer_fail)
                #
                #     # transition for transfer success
                #     transfer_success = {'ntype': 'Simple', 'name': exp['name'] + 'X', 'type': 'transfer_efsm_success'}
                #     transfer_efsm.addTransition(transfer_success)
                #
                #     addAutomata(transfer_efsm)

            else:
                transfer_in_function_name = name + exp['name']
                add_transfer_efsm(transfer_in_function_name)
                # Create a transfer efsm if it already does not exist
                # if exp['name'] not in transfer_efsm_list:
                #     transfer_efsm = EFSM(exp['name'])
                #     transfer_efsm_list.append(exp['name'])
                #     # transfer_efsm.add_transfer(exp)
                #
                #     # transition for transfer event
                #     transfer_event = {'ntype': 'Simple', 'name': exp['name'] + '1', 'type': 'transfer_event'}
                #     transfer_efsm.addTransition(transfer_event)
                #
                #     # transition for transfer fail
                #     transfer_fail = {'ntype': 'Simple', 'name': exp['name'] + 'Fail', 'type': 'transfer_efsm_fail'}
                #     transfer_efsm.addTransition(transfer_fail)
                #
                #     # transition for transfer success
                #     transfer_success = {'ntype': 'Simple', 'name': exp['name'] + 'X', 'type': 'transfer_efsm_success'}
                #     transfer_efsm.addTransition(transfer_success)
                #
                #     addAutomata(transfer_efsm)

            exp['name'] = name + exp['name'] # transfer name is now function name + transfer name to distinguish between same address transfers in different functions
            function.addTransition(exp)

            transfer_success = transfer_in_function_name + 'X'
            transfer_fail = transfer_in_function_name + 'Fail'

            transfer_success_exp = {'ntype': 'Simple', 'name': transfer_success, 'type': 'transfer_success'}
            transfer_fail_exp = {'ntype': 'Simple', 'name': transfer_fail, 'type': 'transfer_fail'}
            next_statement = {'ntype': 'Simple'}
            efsm_fail = {'ntype': 'Simple', 'name': name + 'Fail', 'type': 'efsm_fail'}

            function.addTransition(transfer_fail_exp)
            function.addTransition(efsm_fail)
            function.addTransition(transfer_success_exp)
            function.addTransition(next_statement)

        elif 'type' in exp and exp['type'] == 'mapping_transfer': # check issue #49 in nishantparekh01/test
            #print('Mapping Transfer reached in superFunctionDefinition')
            #print(exp)
            sender_list = exp['sender_list']
            #print(sender_list)
            #asdf

            if exp_index == 0:
                first_transition = {'ntype': 'Simple', 'name': name + '1', 'type': 'first_transition'}
                function.addTransition(first_transition)
                for sender_address in sender_list: # add transfer_efsm for each address if it is not already present
                    sender_address_check = name +sender_address + 'transfer'
                    add_transfer_efsm(sender_address_check)



            else:
                for sender_address in sender_list: # add transfer_efsm for each address if it is not already present
                    sender_address_check = name + sender_address + 'transfer'
                    add_transfer_efsm(sender_address_check)

            for sender_id, sender_address in enumerate(sender_list):
                    transfer_event = name +sender_address + 'transfer'
                    transfer_event_initial = transfer_event + '1'
                    transfer_event_fail = transfer_event + 'Fail'
                    transfer_event_success = transfer_event + 'X'
                    #print('sender id ====', sender_id)

                    if sender_id == 0:
                        transfer_attempt_type = 'sender_transfer_initial'

                        transfer_attempt = {'ntype': 'Simple', 'name': transfer_event_initial, 'sender_index' : sender_id, 'type' : transfer_attempt_type}
                        function.addTransition(transfer_attempt)

                        transfer_fail_exp = {'ntype': 'Simple', 'name': transfer_event_fail, 'type': 'transfer_fail'}
                        efsm_fail = {'ntype': 'Simple', 'name': name + 'Fail', 'type': 'efsm_fail'}
                        function.addTransition(transfer_fail_exp)
                        function.addTransition(efsm_fail)

                        transfer_success_type = 'sender_transfer_success_initial'
                        transfer_success_exp = {'ntype': 'Simple', 'name': transfer_event_success, 'type': transfer_success_type}
                        function.addTransition(transfer_success_exp)


                    else:
                        transfer_attempt_type = 'sender_transfer'

                        transfer_attempt = {'ntype': 'Simple', 'name': transfer_event_initial,
                                            'sender_index': sender_id, 'type': transfer_attempt_type}
                        function.addTransition(transfer_attempt)

                        transfer_fail_exp = {'ntype': 'Simple', 'name': transfer_event_fail, 'type': 'transfer_fail'}
                        efsm_fail = {'ntype': 'Simple', 'name': name + 'Fail', 'type': 'efsm_fail'}
                        function.addTransition(transfer_fail_exp)
                        function.addTransition(efsm_fail)

                        transfer_success_exp = {'ntype': 'Simple', 'name': transfer_event_success,
                                                'type': 'sender_transfer_success'}
                        function.addTransition(transfer_success_exp)

                        if exp_index == len(body) - 1 and sender_id == len(sender_list) - 1:
                            function_complete = {'ntype': 'Simple', 'name': name + 'X', 'type': 'function_complete'}
                            function.addTransition(function_complete)













        elif exp['ntype'] == 'IfStatement':
            true_condition = exp['true_condition']
            false_condition = exp['false_condition']
            # if 'false_condition' in exp:
            #     false_condition = exp['false_condition'] # always present

            true_body = exp['true_body']

            if 'false_body' in exp:
                false_body = exp['false_body']
            true_exp_transition = {'ntype': 'IfStatement', 'kind': 'internal', 'condition': 'true',
                                   'guard_exp': true_condition, 'type': 'true_body_start'}
            # if len(true_body) == 1:
            #     print('True body has only one statement')
            #     true_exp_transition = {'ntype': 'IfStatement', 'kind': 'internal', 'condition': 'true',
            #                            'guard_exp': true_condition, 'type': 'true_body_last'}
            # else:
            #     true_exp_transition = {'ntype': 'IfStatement', 'kind': 'internal', 'condition': 'true',
            #                        'guard_exp': true_condition, 'type': 'true_body_start'}
            if 'false_body' in exp:
                false_exp_transition = {'ntype': 'IfStatement', 'kind': 'internal', 'condition': 'false',
                                    'guard_exp': false_condition, 'type': 'false_body_start'}
            else:
                false_exp_transition = {'ntype': 'IfStatement', 'kind': 'internal', 'condition': 'false','guard_exp': false_condition, 'type': 'false_body_absent'}

            function.addTransition(true_exp_transition)
            for index, stmnt in enumerate(true_body): # add transitions for each statement in the true body
                if index == len(true_body) - 1:
                    stmnt['type'] = 'true_body_last'
                    function.addTransition(stmnt)
                else:
                    if 'exp' or 'expression' in stmnt:
                        if 'exp' in exp:
                            #     exp_node = exp['exp']
                            # # elif 'expression' in exp:
                            # #     exp_node = exp['expression']
                            #
                            #     for ignore_var in ignore_list:
                            #         if in_ignore_list(exp_node, ignore_var):
                            #             exp['exp'] = None
                            #             function.addTransition(exp)
                            #         else:
                            #             function.addTransition(exp)
                            process_in_ignore_list(stmnt, 'exp', ignore_list, function)

                        elif 'expression' in exp:
                            # exp_node = exp['expression']
                            # for ignore_var in ignore_list:
                            #     if in_ignore_list(exp_node, ignore_var):
                            #         exp['expression'] = None
                            #         function.addTransition(exp)
                            #     else:
                            #         function.addTransition(exp)
                            process_in_ignore_list(stmnt, 'expression', ignore_list, function)
                    #function.addTransition(stmnt)
                if stmnt['ntype'] == 'FunctionCall':
                    if index == len(true_body) - 1: # flag the last statement in the true body, if statement is a function call
                        function_complete = {'ntype': 'Simple', 'name': stmnt['name'] + 'X', 'type': 'true_body_last'}
                        #function_fail = {'ntype': 'Simple', 'name': stmnt['name'] + 'Fail', 'type': 'function_fail'}
                        #print('transition added', function_complete)
                        #print('fail transition added', function_fail)
                        #function.addTransition(function_fail)
                        function_call_name = stmnt['name']
                        if check_transfer_in_function(function_call_name):
                            function_fail = {'ntype': 'Simple', 'name': stmnt['name'] + 'Fail', 'type': 'function_fail'}
                            function.addTransition(function_fail)
                        function.addTransition(function_complete)
                    else:
                        function_complete = {'ntype': 'Simple', 'name': stmnt['name'] + 'X', 'type': 'function_complete'}
                        function_fail = {'ntype': 'Simple', 'name': stmnt['name'] + 'Fail', 'type': 'function_fail'}
                        #function.addTransition(function_fail)
                        if check_transfer_in_function(function_call_name):
                            function_fail = {'ntype': 'Simple', 'name': stmnt['name'] + 'Fail', 'type': 'function_fail'}
                            function.addTransition(function_fail)

                        function.addTransition(function_complete)


            function.addTransition(false_exp_transition) # add transition for false condition. For both cases when false body is present/absent


            if 'false_body' in exp: # if false body is present
                for index, stmnt in enumerate(false_body): # add transitions for each statement in the false body
                    if index == len(false_body) - 1:  # if it is the last statement in the false body
                        stmnt['type'] = 'false_body_last'
                        function.addTransition(stmnt)
                        if exp_index == len(body) - 1: # and if it is the last transition in the body
                            function_complete = {'ntype': 'Simple','name': name + 'X', 'type': 'function_complete'}
                            function.addTransition(function_complete)

                    else:
                        function.addTransition(stmnt)
                    if stmnt['ntype'] == 'FunctionCall':
                        if index == len(false_body) - 1: # flag the last statement in the false body, if statement is a function call
                            function_complete = {'ntype': 'Simple', 'name': stmnt['name'] + 'X', 'type': 'false_body_last'}
                            function_call_name = stmnt['name']
                            if check_transfer_in_function(function_call_name):
                                function_fail = {'ntype': 'Simple', 'name': stmnt['name'] + 'Fail', 'type': 'function_fail'}
                                function.addTransition(function_fail)
                            # else:
                            # function_fail = {'ntype': 'Simple', 'name': stmnt['name'] + 'Fail', 'type': 'function_fail'}
                            # function.addTransition(function_fail)
                            function.addTransition(function_complete)

                        else:
                            function_complete = {'ntype': 'Simple', 'name': stmnt['name'] + 'X', 'type': 'function_complete'}
                            function_fail = {'ntype': 'Simple', 'name': stmnt['name'] + 'Fail', 'type': 'function_fail'}
                            function.addTransition(function_fail)
                            function.addTransition(function_complete)
            else:
                # if false body is absent and it was the last transition
                if exp_index == len(body) - 1:
                    function_complete = {'ntype': 'Simple', 'name': name + 'X', 'type': 'function_complete'}
                    function.addTransition(function_complete)

        elif exp['ntype'] == 'FunctionCall' and exp['name'] == 'require':
            # exp_node = exp['args']
            # for ignore_var in ignore_list:
            #     if in_ignore_list(exp_node, ignore_var):
            #         exp['args'] = None
            #         function.addTransition(exp)
            #     else:
            #         function.addTransition(exp)
            # if exp_index != 0:
            #     print('exp_index', exp_index)
            process_in_ignore_list(exp, 'args', ignore_list, function, transition_type = 'require_true', efsm_name = name)


            # else:
            #     process_in_ignore_list(exp, 'args', ignore_list, function)
            #function.addTransition(exp)

            # Parameter assignment place here so that it is called after the require statement if any require statement is present
            if param_assigned == False:
                for param, param_type in params.items():
                    #print(param, param_type, 'param and param_type')
                    if param_type in VariableComponent['EnumVariables']:
                        # generate xml expression where param = param_type[0] | param_type[1] | param_type[2] | ...
                        guard_exp = wmodify_assignment(param, "==", VariableComponent['EnumVariables'][param_type],
                                                       **{'ntype': 'ParameterDeclarationStatement',
                                                          'kind': 'AssignmentCheck'})
                       # print(ET.tostring(guard_exp, encoding='unicode', method='xml'))
                        param_assignment = {'ntype': 'Simple', 'guard_exp': guard_exp, 'type': 'param_assignment'}
                        function.addTransition(param_assignment)

                    # work on this part later
                    elif param_type == 'uint' or param_type == 'uint256' or param_type == 'bytes32':
                        rhs_list  = ['0','1']
                        guard_exp = wmodify_assignment(param, "==", rhs_list, **{'ntype': 'ParameterDeclarationStatement',
                                                                          'kind': 'AssignmentCheck'})
                        param_assignment = {'ntype': 'Simple', 'guard_exp': guard_exp, 'type': 'param_assignment'}
                        function.addTransition(param_assignment)
                    param_assigned = True


        elif exp['ntype'] == 'Assignment' and exp['kind'] == 'structConstructorCall':
            #print('Struct Constructor Call')
            for attr_assignments in exp['exp']:
                #function.addTransition(attr_assignments)
                #print(attr_assignments)
                 exp = {'ntype': 'Assignment', 'kind': 'simple', 'exp': attr_assignments}
                 #print(exp)
                 process_in_ignore_list(    exp, 'exp', ignore_list, function)
                 #function.addTransition(exp)
                 #print('assignment added')
            #print(asdf)

        else:
            if 'exp' in exp or 'expression' in exp:
                #exp_string = ET.tostring(exp['exp'], encoding='unicode', method='xml')
                if 'exp' in exp:
                #     exp_node = exp['exp']
                # # elif 'expression' in exp:
                # #     exp_node = exp['expression']
                #
                #     for ignore_var in ignore_list:
                #         if in_ignore_list(exp_node, ignore_var):
                #             exp['exp'] = None
                #             function.addTransition(exp)
                #         else:
                #             function.addTransition(exp)
                    process_in_ignore_list(exp, 'exp', ignore_list, function)

                elif 'expression' in exp:
                    # exp_node = exp['expression']
                    # for ignore_var in ignore_list:
                    #     if in_ignore_list(exp_node, ignore_var):
                    #         exp['expression'] = None
                    #         function.addTransition(exp)
                    #     else:
                    #         function.addTransition(exp)
                    process_in_ignore_list(exp, 'expression', ignore_list, function)


    addAutomata(function)
    return Supremica

ignore_list = ['pot', 'bet',  'withdrawable_player', 'withdrawable_operator',  'tmp', 'withdrawable_buyer', 'withdrawable_supplier']


def superVariableDeclarationStatement(packet):
    pass

################ Adding framework behaviour ################################################

################ Adding in_ignore_list ################################################

def in_ignore_list(element, search_string):
    # Check if the search string is in the element's text
    if element.text and search_string in element.text:
        return True

    # Check if the search string is in the element's tail text
    if element.tail and search_string in element.tail:
        return True

    # Check if the search string is in any of the element's attributes
    for attribute in element.attrib.values():
        if search_string in attribute:
            return True

    # Recursively check all child elements
    for child in element:
        if in_ignore_list(child, search_string):
            return True

    # If none of the conditions are met
    return False

################ Processing if in in_ignore_list ################################################

def process_in_ignore_list(exp, exp_key, ignore_list, function, **kwargs):
    transition_type = kwargs.get('transition_type', None)
    efsm_name = kwargs.get('efsm_name', None)

    false_exp = {}
    print('Expression:--',exp)
    print(exp)
    print(exp[exp_key])
    exp_node = exp[exp_key]
    print('Exp Node---', exp_node)

    for ignore_var in ignore_list:
        if in_ignore_list(exp_node, ignore_var):
            print('Im hereeee')
            exp[exp_key] = None
            break

    if transition_type  and initial_statement_added == True and exp[exp_key] != None:
            exp['type'] = transition_type
            print('Transition Type-----------', transition_type)
            require_condition = exp['args']
            require_condition_false = ET.Element("UnaryExpression", Operator="!")
            require_condition_false.append(require_condition)
            function_fail = efsm_name + 'Fail'
            false_exp = {'ntype': 'Simple','name':function_fail, 'guard_exp': require_condition_false, 'type': 'require_false' }


    function.addTransition(exp)
    if false_exp != {}:
        print("False Exp", false_exp)
        function.addTransition(false_exp)



################ Checking through final_sol_list ################################################

#print(final_sol_list)

def check_transfer_in_function(function_name):
    for node in final_sol_list:
        if node['nodeType'] == 'FunctionDefinition' and node['name'] == function_name:
            # convert node into a string
            node_string = str(node) # convert the node into a string
            # check if the function name is present in the node_string
            if 'transfer' in node_string:
                #print('Hurrah! Transfer present in the function: ', function_name)
                #print(node['name'])
                return True
            else:
                #print('Transfer not present in the function: ', function_name)
                #print(node['name'])
                return False



#check_transfer_in_function('operatorWins')