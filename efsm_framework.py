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

Supremica = {}

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

# list for transfer efsms
transfer_efsm_list = []


class EFSM:
    def __init__(self,
                 name):  # This is to create the structure for each efsm. Right for modifiers. Later for all functions
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

            # print('Expression type==',type(expression))
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
                    # print(expression['name'])
                    # action_exp = str(expression['name'] + '(' + expression['args'] + ')')
                    events.append(expression['name'])

            elif expression['ntype'] == 'Simple':
                if 'name' in expression:
                    events.append(expression['name'])
                    if expression['type'] == 'transfer_fail':
                        target_index = 'S0'

            elif expression['ntype'] == 'Assignment':
                if expression['kind'] == 'conditional':
                    guard_exp = expression['condition']
                    true_body = expression['lhs'] + ' = ' + expression['true_exp']
                    false_body = expression['lhs'] + ' = ' + expression['false_exp']
                    true_expression_dict = {'ntype': 'Assignment', 'kind': 'simple', 'exp': true_body}
                    false_expression_dict = {'ntype': 'Assignment', 'kind': 'simple', 'exp': false_body}
                    # print(true_expression_dict)
                    # print(false_expression_dict)
                    # self.addTransition(true_expression_dict)
                    # self.addTransition(false_expression_dict)
                elif expression['kind'] == 'simple':
                    # print(expression['exp'])
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
                        # guard_exp = ET.tostring(expression['guard_exp'], encoding='unicode', method='xml')
                        # action_exp = expression['exp']  # Assumption: only one expression in the body
                    elif expression['condition'] == 'false':
                        guard_exp = expression['guard_exp']
                        # guard_exp = ET.tostring(expression['guard_exp'], encoding='unicode', method='xml')
                        # action_exp = expression['exp'] # Assumption: only one expression in the body
                else:
                    true_condition = expression['true_condition']
                    false_condition = expression['false_condition']

                    true_body = expression['true_body']
                    false_body = expression['false_body']
                    # condition_negation = "!" + "(" + condition + ")"
                    true_exp_transition = {'ntype': 'IfStatement', 'kind': 'internal', 'condition': 'true',
                                           'guard_exp': true_condition, 'exp': true_body}
                    false_exp_transition = {'ntype': 'IfStatement', 'kind': 'internal', 'condition': 'false',
                                            'guard_exp': false_condition, 'exp': false_body}
                    self.addTransition(true_exp_transition)
                    self.addTransition(false_exp_transition)

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
            Components[mod]['edge_list']['t0']['events'].append(self.name + '1')

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
    for exp in body:
        modifier.addTransition(exp)
    # print("MODIFIER  ",modifier.efsm)
    addAutomata(modifier)
    return Supremica


def superFunctionDefinition(packet):
    name = packet['name']
    params = packet['params']
    body = packet['body']
    modifiers = packet['modifiers']

    # Create EFSM instance of function
    function = EFSM(name)

    # Add function name to invoked modifiers
    # print(name, modifiers)
    if modifiers:
        function.addModifierInvocation(modifiers)

    for exp in body:
        if 'type' in exp and exp['type'] == 'transfer':

            # Create a transfer efsm if it already does not exist
            if exp['name'] not in transfer_efsm_list:
                transfer_efsm = EFSM(exp['name'])
                transfer_efsm_list.append(exp['name'])
                #transfer_efsm.add_transfer(exp)

                # transition for transfer event
                transfer_event = {'ntype': 'Simple', 'name': exp['name'] + '1', 'type': 'transfer_event'}
                transfer_efsm.addTransition(transfer_event)

                # transition for transfer fail
                transfer_fail = {'ntype': 'Simple', 'name': exp['name'] + 'Fail', 'type': 'transfer_fail'}
                transfer_efsm.addTransition(transfer_fail)

                # transition for transfer success
                transfer_success = {'ntype': 'Simple', 'name': exp['name'] + 'X', 'type': 'transfer_success'}
                transfer_efsm.addTransition(transfer_success)


                addAutomata(transfer_efsm)

            function.addTransition(exp)

            transfer_success = exp['name'] + 'X'
            transfer_fail = exp['name'] + 'Fail'
            
            transfer_success_exp = {'ntype': 'Simple', 'name': transfer_success, 'type': 'transfer_success'}
            transfer_fail_exp = {'ntype': 'Simple', 'name': transfer_fail, 'type': 'transfer_fail'}

            next_statement = {'ntype': 'Simple'}


            function.addTransition(transfer_fail_exp)
            function.addTransition(transfer_success_exp)
            function.addTransition(next_statement)

        else:
            function.addTransition(exp)

    # for modifier_name in modifiers:
    #     modifier_name.addEvent(name)

    addAutomata(function)
    return Supremica


def superVariableDeclarationStatement(packet):
    pass

################ Adding framework behaviour ################################################

# Assign Sender


# transfer function 


# for k,v in Supremica.items():
#     print(k,v)
