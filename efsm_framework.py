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
# Supremica['Variables'] = {}

class EFSM:
    def __init__(self, name):  # This is to create the structure for each efsm. Right for modifiers. Later for all functions
        self.name = name
        self.efsm = {}
        #efsm = self.efsm

        self.efsm['node_list'] = {}
        self.node_list = self.efsm['node_list']

        self.efsm['edge_list'] = {}
        self.edge_list = self.efsm['edge_list']
        self.i = 0 

    def addTransition(self, expression):

        source_index = None
        target_index = None
        events = []
        guard_exp = None
        action_exp = None
        evaluate_exp = None
        evaluate_exp = expression  # This should be derived if 'FunctionCall' is require.

        # we have to check the ntype of expression and then add the transition accordingly
        # we should check this by creating a function call and then checking the ntype of the expression
        if expression != False: # This is for the placeholder statement

            print('Expression type==',type(expression))
            if expression['ntype'] == 'FunctionCall':
                if expression['name'] == 'require':
                    # assuming that require has only one argument
                    guard_exp = expression['args']
                #elif expression['name'] == 'keccak256':
                else:
                    #print(expression['name'])
                    #action_exp = str(expression['name'] + '(' + expression['args'] + ')')
                    events.append(expression['name'])

            elif expression['ntype'] == 'Assignment':
                if expression['kind'] == 'conditional':
                    guard_exp = expression['condition']
                    true_body = expression['lhs'] + ' = ' + expression['true_exp']
                    false_body = expression['lhs'] + ' = ' + expression['false_exp']
                    true_expression_dict = {'ntype' : 'Assignment', 'kind' : 'simple',  'exp' : true_body}
                    false_expression_dict = {'ntype' : 'Assignment', 'kind' : 'simple',  'exp' : false_body}
                    #print(true_expression_dict)
                    #print(false_expression_dict)
                    #self.addTransition(true_expression_dict)
                    #self.addTransition(false_expression_dict)
                elif expression['kind'] == 'simple':
                    action_exp = expression['exp']
            elif expression['ntype'] == 'VariableDeclarationStatement':
                if expression['kind'] == 'conditional':
                    #condition = expression['condition']
                    #true_body = expression['name'] + ' == ' + expression['true_exp']
                    #false_body = expression['name'] + ' == ' + expression['false_exp']
                    #guard_exp = str("(" + condition + " & " + true_body + ") | (" + "!" + "(" + condition + ")" + " & " + false_body + ")")
                    guard_exp = expression['expression']
            elif expression['ntype'] == 'IfStatement':
                if 'kind' in expression and expression['kind'] == 'internal':
                    if expression['condition'] == 'true':
                        guard_exp = expression['guard_exp']
                        action_exp = expression['exp']  # Assumption: only one expression in the body
                    elif expression['condition'] == 'false':
                        guard_exp = expression['guard_exp']
                        action_exp = expression['exp'] # Assumption: only one expression in the body
                else:
                    true_condition = expression['true_condition']
                    false_condition = expression['false_condition']

                    true_body = expression['true_body']
                    false_body = expression['false_body']
                    #condition_negation = "!" + "(" + condition + ")"
                    true_exp_transition = {'ntype': 'IfStatement', 'kind': 'internal', 'condition' : 'true', 'guard_exp' : true_condition, 'exp': true_body}
                    false_exp_transition = {'ntype': 'IfStatement', 'kind': 'internal', 'condition' : 'false', 'guard_exp': false_condition, 'exp': false_body}
                    self.addTransition(true_exp_transition)
                    self.addTransition(false_exp_transition)






        transition = {'source_index' : source_index,
                                   'target_index' : target_index,
                                   'events'       : events,
                                   'guard_exp'    : guard_exp,
                                   'action_exp'   : action_exp,
                                   'evaluate_exp' : evaluate_exp
                                   }

        self.edge_list[f't{self.i}'] = transition
        self.i += 1

        
    def addModifierInvocation(self, modifiers):
        # Assumption that modifier right now has only one statement, which is the require statement.
        # issue #1 in nishantparekh01/casino_conversion
        for m in modifiers:
            # if m in Components:
            Components[m]['edge_list']['t0']['events'].append(self.name)





def addAutomata(efsm):
    global Components
    Components[efsm.name] = efsm.efsm

def superModifierDefinition(packet):
    # must return a dictionary
    global Supremica

    name = packet['name'] # name of modifier
    # fill the name here. Create a new efsm
    # To create the ast, for each level we need a function

    params = packet['params']
    # Use parameters in whichever way

    body = packet['body'] # list of expressions
    # Generate transitions using expressions here.

    # Create modifier object
    modifier = EFSM(name)
    for exp in body:
        modifier.addTransition(exp)
    #print("MODIFIER  ",modifier.efsm)
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
    #print(name, modifiers)
    if modifiers:
        function.addModifierInvocation(modifiers)

    for exp in body:
        function.addTransition(exp)

    # for modifier_name in modifiers:
    #     modifier_name.addEvent(name)

    addAutomata(function)
    return Supremica

################ Adding framework behaviour ################################################

# Assign Sender


# transfer function 


# for k,v in Supremica.items():
#     print(k,v)