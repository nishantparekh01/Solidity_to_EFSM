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

                elif 'type' in expression and expression['type'] == 'param_assignment':
                    guard_exp = expression['guard_exp']


            elif expression['ntype'] == 'Assignment':
                if expression['kind'] == 'conditional':
                    guard_exp = expression['condition']
                    true_body = expression['lhs'] + ' = ' + expression['true_exp']
                    false_body = expression['lhs'] + ' = ' + expression['false_exp']
                    true_expression_dict = {'ntype': 'Assignment', 'kind': 'simple', 'exp': true_body}
                    false_expression_dict = {'ntype': 'Assignment', 'kind': 'simple', 'exp': false_body}

                    # self.addTransition(true_expression_dict)
                    # self.addTransition(false_expression_dict)
                elif expression['kind'] == 'simple':
                    # if expression['exp'] != None:
                    #     action_exp = expression['exp']
                    # else:
                    #     action_exp = None
                    action_exp = expression['exp']
                    # action_exp = ET.tostring(expression['exp'], encoding='unicode', method='xml')


            elif expression['ntype'] == 'VariableDeclarationStatement':
                if expression['kind'] == 'conditional':
                    # condition = expression['condition']
                    # true_body = expression['name'] + ' == ' + expression['true_exp']
                    # false_body = expression['name'] + ' == ' + expression['false_exp']
                    # guard_exp = str("(" + condition + " & " + true_body + ") | (" + "!" + "(" + condition + ")" + " & " + false_body + ")")
                    guard_exp = expression['expression']
                    # guard_exp = ET.tostring(expression['expression'], encoding='unicode', method='xml')
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
            for declared_address in AddressVariables.keys():
                print(mapping_name + '_'+ declared_address)

        gyg = gyg - 2

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
            modifier.addTransition(exp)


    # Add modifier to the global dictionary
    modifier_objects_dict[name] = modifier

    addAutomata(modifier)
    return Supremica


def superFunctionDefinition(packet):
    global false_body
    name = packet['name']
    params = packet['params']
    global param_assigned
    param_assigned = False
    body = packet['body']
    modifiers = packet['modifiers']

    # Create EFSM instance of function
    function = EFSM(name)

    # Add function name to invoked modifiers
    if modifiers:
        function.addModifierInvocation(modifiers)

    # Add transitions to the function based on parameters and its respective values

    for exp_index, exp in enumerate(body):

        if 'type' in exp and exp['type'] == 'transfer':
            if exp_index == 0:
                first_transition = {'ntype': 'Simple', 'name': name + '1', 'type': 'first_transition'}
                function.addTransition(first_transition)
                if exp['name'] not in transfer_efsm_list:
                    transfer_efsm = EFSM(exp['name'])
                    transfer_efsm_list.append(exp['name'])
                    # transfer_efsm.add_transfer(exp)

                    # transition for transfer event
                    transfer_event = {'ntype': 'Simple', 'name': exp['name'] + '1', 'type': 'transfer_event'}
                    transfer_efsm.addTransition(transfer_event)

                    # transition for transfer fail
                    transfer_fail = {'ntype': 'Simple', 'name': exp['name'] + 'Fail', 'type': 'transfer_efsm_fail'}
                    transfer_efsm.addTransition(transfer_fail)

                    # transition for transfer success
                    transfer_success = {'ntype': 'Simple', 'name': exp['name'] + 'X', 'type': 'transfer_efsm_success'}
                    transfer_efsm.addTransition(transfer_success)

                    addAutomata(transfer_efsm)

            else:
                # Create a transfer efsm if it already does not exist
                if exp['name'] not in transfer_efsm_list:
                    transfer_efsm = EFSM(exp['name'])
                    transfer_efsm_list.append(exp['name'])
                    # transfer_efsm.add_transfer(exp)

                    # transition for transfer event
                    transfer_event = {'ntype': 'Simple', 'name': exp['name'] + '1', 'type': 'transfer_event'}
                    transfer_efsm.addTransition(transfer_event)

                    # transition for transfer fail
                    transfer_fail = {'ntype': 'Simple', 'name': exp['name'] + 'Fail', 'type': 'transfer_efsm_fail'}
                    transfer_efsm.addTransition(transfer_fail)

                    # transition for transfer success
                    transfer_success = {'ntype': 'Simple', 'name': exp['name'] + 'X', 'type': 'transfer_efsm_success'}
                    transfer_efsm.addTransition(transfer_success)

                    addAutomata(transfer_efsm)



            function.addTransition(exp)

            transfer_success = exp['name'] + 'X'
            transfer_fail = exp['name'] + 'Fail'

            transfer_success_exp = {'ntype': 'Simple', 'name': transfer_success, 'type': 'transfer_success'}
            transfer_fail_exp = {'ntype': 'Simple', 'name': transfer_fail, 'type': 'transfer_fail'}
            next_statement = {'ntype': 'Simple'}
            efsm_fail = {'ntype': 'Simple', 'name': name + 'Fail', 'type': 'efsm_fail'}

            function.addTransition(transfer_fail_exp)
            function.addTransition(efsm_fail)
            function.addTransition(transfer_success_exp)
            function.addTransition(next_statement)

        elif exp['ntype'] == 'IfStatement':
            true_condition = exp['true_condition']
            if 'false_condition' in exp:
                false_condition = exp['false_condition']

            true_body = exp['true_body']

            if 'false_body' in exp:
                false_body = exp['false_body']

            true_exp_transition = {'ntype': 'IfStatement', 'kind': 'internal', 'condition': 'true',
                                   'guard_exp': true_condition, 'type': 'true_body_start'}
            if 'false_body' in exp:
                false_exp_transition = {'ntype': 'IfStatement', 'kind': 'internal', 'condition': 'false',
                                    'guard_exp': false_condition, 'type': 'false_body_start'}

            function.addTransition(true_exp_transition)
            for index, stmnt in enumerate(true_body):
                function.addTransition(stmnt)
                if stmnt['ntype'] == 'FunctionCall':
                    if index == len(true_body) - 1:
                        function_complete = {'ntype': 'Simple', 'name': stmnt['name'] + 'X', 'type': 'true_body_last'}
                        function_fail = {'ntype': 'Simple', 'name': stmnt['name'] + 'Fail', 'type': 'function_fail'}
                        function.addTransition(function_fail)
                        function.addTransition(function_complete)
                    else:
                        function_complete = {'ntype': 'Simple', 'name': stmnt['name'] + 'X', 'type': 'function_complete'}
                        function_fail = {'ntype': 'Simple', 'name': stmnt['name'] + 'Fail', 'type': 'function_fail'}
                        function.addTransition(function_fail)
                        function.addTransition(function_complete)

            if 'false_body' in exp:
                function.addTransition(false_exp_transition)

            if 'false_body' in exp:
                for index, stmnt in enumerate(false_body):
                    function.addTransition(stmnt)
                    if stmnt['ntype'] == 'FunctionCall':
                        if index == len(false_body) - 1:
                            function_complete = {'ntype': 'Simple', 'name': stmnt['name'] + 'X', 'type': 'false_body_last'}
                            function_fail = {'ntype': 'Simple', 'name': stmnt['name'] + 'Fail', 'type': 'function_fail'}
                            function.addTransition(function_fail)
                            function.addTransition(function_complete)

                        else:
                            function_complete = {'ntype': 'Simple', 'name': stmnt['name'] + 'X', 'type': 'function_complete'}
                            function_fail = {'ntype': 'Simple', 'name': stmnt['name'] + 'Fail', 'type': 'function_fail'}
                            function.addTransition(function_fail)
                            function.addTransition(function_complete)

        elif exp['ntype'] == 'FunctionCall' and exp['name'] == 'require':
            # exp_node = exp['args']
            # for ignore_var in ignore_list:
            #     if in_ignore_list(exp_node, ignore_var):
            #         exp['args'] = None
            #         function.addTransition(exp)
            #     else:
            #         function.addTransition(exp)
            process_in_ignore_list(exp, 'args', ignore_list, function)
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
                        param_assigned = True

        elif exp['ntype'] == 'Assignment' and exp['kind'] == 'structConstructorCall':
            print('Struct Constructor Call')
            for attr_assignments in exp['exp']:
                #function.addTransition(attr_assignments)
                #print(attr_assignments)
                 exp = {'ntype': 'Assignment', 'kind': 'simple', 'exp': attr_assignments}
                 print(exp)
                 process_in_ignore_list(    exp, 'exp', ignore_list, function)
                 #function.addTransition(exp)
                 print('assignment added')
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

ignore_list = ['pot', 'tmp', 'bet']


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

def process_in_ignore_list(exp, exp_key, ignore_list, function):
    exp_node = exp[exp_key]
    for ignore_var in ignore_list:
        if in_ignore_list(exp_node, ignore_var):
            exp[exp_key] = None
            break

    function.addTransition(exp)