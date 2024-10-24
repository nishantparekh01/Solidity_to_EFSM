# importing modules
import xml.etree.ElementTree as ET

# Initial node = S0
INITIAL_NODE = 'S0'

# to check if a variable with str in it can be converted to an int or not
def is_integer(variable):
    if isinstance(variable, int):
        return True
    if isinstance(variable, str):
        try:
            int(variable)
            return True
        except ValueError:
            return False
    return False

# A function to add nodes to node_list
def add_nodes_to_xml(node_list):
    # Exameple of node_list = ['S0', 'S1', 'S2', 'S3']
    NodeList = ET.Element("NodeList")
    for node in node_list:
        if node == INITIAL_NODE:
            SimpleNode = ET.SubElement(NodeList, "SimpleNode", Initial = "true",  Name = node) # Initial = "true" is added to the first node
            EventList = ET.SubElement(SimpleNode, "EventList")
            SimpleIdentifier_accepting = ET.SubElement(EventList, "SimpleIdentifier", Name = ":accepting")
        else:
            SimpleNode = ET.SubElement(NodeList, "SimpleNode",  Name = node)

    return  NodeList


def add_transition_to_xml(transition):
    # Example of transition = {'action_exp': 'action', 'guard_exp': 'guard', 'source_index': 'S0', 'target_index': 'S1', 'event': 'event'}
    Edge = ET.Element("Edge", Source = transition['source_index'], Target = transition['target_index'])
    LabelBlock = ET.SubElement(Edge, "LabelBlock")
    if 'event' in transition:
        event_SimpleIdentifier = ET.SubElement(LabelBlock, "SimpleIdentifier", Name=transition['event'])
    else:
        for event in transition['events']:
            event_SimpleIdentifier = ET.SubElement(LabelBlock, "SimpleIdentifier", Name=event)

    GuardActionBlock = ET.SubElement(Edge, "GuardActionBlock")
    # check if guard_exp is present
    if transition['guard_exp'] is not None:
        Guard = ET.SubElement(GuardActionBlock, "Guards")
        guard_exp_xml = transition['guard_exp']
        Guard.append(guard_exp_xml)
    if transition['action_exp'] is not None:
        Action = ET.SubElement(GuardActionBlock, "Actions")
        action_exp_xml = transition['action_exp']
        Action.append(action_exp_xml)

    return Edge
def wmodify_assignment(lhs, op, rhs, **info):
    #print(lhs, op, rhs)
    #print(type(rhs))
    #print(rhs)
    if info:
        if info['ntype'] == 'VariableDeclarationStatement':
            if info['kind'] == 'conditional':
                # lhs = name, secret
                # op = ==
                # rhs = HEADS
                true_condition = info['condition']

                # creating false condition by appending true condition to unaryOperator = "!"
                false_condition = ET.Element("UnaryExpression", Operator = "!")
                false_condition.append(true_condition)

                lhs_trueAssignment = wmodify_assignment(true_condition, "&", info['true_exp'], **{'ntype': 'VariableDeclarationStatement', 'kind': 'AssignmentCheck', 'variableAssigned' : info['name']})

                rhs_falseAssignment = wmodify_assignment(false_condition, "&", info['false_exp'], **{'ntype': 'VariableDeclarationStatement', 'kind': 'AssignmentCheck', 'variableAssigned' : info['name']})

                final_exp = wmodify_assignment(lhs_trueAssignment, "|", rhs_falseAssignment)

                #print(print(ET.tostring(final_exp, encoding='unicode', method='xml')))
                return final_exp

            if info['kind'] == 'AssignmentCheck':
                BinaryExpression = ET.Element("BinaryExpression", Operator=str(op))
                BinaryExpression.append(lhs)

                lhs_assignment = ET.Element("UnaryExpression", Operator = "'")
                SimpleIdentifier = ET.SubElement(lhs_assignment, "SimpleIdentifier", Name = str(info['variableAssigned']))

                rhs_wmod = wmodify_assignment(lhs_assignment, "==", str(rhs))
                BinaryExpression.append(rhs_wmod)
                #print(print(ET.tostring(BinaryExpression, encoding='unicode', method='xml')))
                return BinaryExpression

        elif info['ntype'] == 'ParameterDeclarationStatement':

            if info['kind'] == 'AssignmentCheck':
                # lhs = param
                # op = ==
                # rhs = ['HEADS', 'TAILS']
                # expression to be geenrate = param' == 'HEADS' | param' == 'TAILS'

                root_expression = ET.Element("BinaryExpression", Operator = "|")
                previous_expression = None

                if len(rhs) == 2:
                    binary_expression1 = ET.Element("BinaryExpression", Operator="==")
                    lhs_assignment1 = ET.SubElement(binary_expression1, "UnaryExpression", Operator="'")
                    ET.SubElement(lhs_assignment1, "SimpleIdentifier", Name=lhs)
                    ET.SubElement(binary_expression1, "SimpleIdentifier", Name=rhs[0])

                    # Create the second binary expression
                    binary_expression2 = ET.Element("BinaryExpression", Operator="==")
                    lhs_assignment2 = ET.SubElement(binary_expression2, "UnaryExpression", Operator="'")
                    ET.SubElement(lhs_assignment2, "SimpleIdentifier", Name=lhs)
                    ET.SubElement(binary_expression2, "SimpleIdentifier", Name=rhs[1])

                    # Create an OR binary expression combining the two
                    root_expression.append(binary_expression1)
                    root_expression.append(binary_expression2)
                else:
                    for value in rhs:
                        BinaryExpression = ET.Element("BinaryExpression", Operator = "==")
                        lhs_assignment = ET.SubElement(BinaryExpression, "UnaryExpression", Operator = "'")
                        ET.SubElement(lhs_assignment, "SimpleIdentifier", Name = str(lhs))

                        # creating rhs
                        ET.SubElement(BinaryExpression, "SimpleIdentifier", Name = str(value))

                        if previous_expression is None:
                            previous_expression = BinaryExpression
                        else:
                            or_expression = ET.Element("BinaryExpression", Operator = "|")
                            or_expression.append(previous_expression)
                            or_expression.append(BinaryExpression)
                            previous_expression = or_expression

                    root_expression.append(previous_expression)

                return root_expression





    else:
        if isinstance(rhs, dict) and isinstance(lhs, str):

            BinaryExpression = ET.Element("BinaryExpression", Operator = str(op))
            SimpleIdentifier = ET.SubElement(BinaryExpression, "SimpleIdentifier", Name = str(lhs))
            SimpleIdentifier = ET.SubElement(BinaryExpression, "SimpleIdentifier", Name = str(rhs['args']))


        # if the binary expression is a simple assignment
        elif isinstance(rhs, str) and isinstance(lhs, str):
            if is_integer(rhs) and not is_integer(lhs):
                BinaryExpression = ET.Element("BinaryExpression", Operator = str(op))
                SimpleIdentifier = ET.SubElement(BinaryExpression, "SimpleIdentifier", Name = str(lhs))
                IntConstant = ET.SubElement(BinaryExpression, "IntConstant", Value = str(rhs))
            elif is_integer(lhs) and is_integer(rhs):
                BinaryExpression = ET.Element("BinaryExpression", Operator = str(op))
                IntConstant = ET.SubElement(BinaryExpression, "IntConstant", Value = str(lhs))
                IntConstant = ET.SubElement(BinaryExpression, "IntConstant", Value = str(rhs))
            else:
                BinaryExpression = ET.Element("BinaryExpression", Operator = str(op))
                SimpleIdentifier = ET.SubElement(BinaryExpression, "SimpleIdentifier", Name = str(lhs))
                SimpleIdentifier = ET.SubElement(BinaryExpression, "SimpleIdentifier", Name = str(rhs))

        # if rhs is xml element then append it to the BinaryExpression
        elif isinstance(rhs, ET.Element) and isinstance(lhs, ET.Element):

            BinaryExpression = ET.Element("BinaryExpression", Operator = str(op))
            BinaryExpression.append(lhs)
            BinaryExpression.append(rhs)
            # SimpleIdentifier_lhs = ET.SubElement(BinaryExpression, tag=lhs)
            # SimpleIdentifier_rhs = ET.SubElement(BinaryExpression, tag =rhs)


        elif isinstance(rhs, ET.Element) and isinstance(lhs, str):
            BinaryExpression = ET.Element("BinaryExpression", Operator = str(op))
            SimpleIdentifier = ET.SubElement(BinaryExpression, "SimpleIdentifier", Name = str(lhs))
            BinaryExpression.append(rhs)
            #BinaryExpression.append(rhs)
            #print(ET.tostring(BinaryExpression, encoding='unicode', method='xml'))
            #return str(ET.tostring(BinaryExpression, encoding='unicode', method='xml'))
            return BinaryExpression

        elif isinstance(rhs, str) and isinstance(lhs, ET.Element):

            if is_integer(rhs):
                BinaryExpression = ET.Element("BinaryExpression", Operator=str(op))
                BinaryExpression.append(lhs)
                IntConstant = ET.SubElement(BinaryExpression, "IntConstant", Value=str(rhs))
            else:
                BinaryExpression = ET.Element("BinaryExpression", Operator = str(op))
                BinaryExpression.append(lhs)
                SimpleIdentifier = ET.SubElement(BinaryExpression, "SimpleIdentifier", Name = str(rhs))
            #BinaryExpression.append(rhs)
            #print(ET.tostring(BinaryExpression, encoding='unicode', method='xml'))
            #return str(ET.tostring(BinaryExpression, encoding='unicode', method='xml'))
            return BinaryExpression

        #return str(ET.tostring(BinaryExpression, encoding='unicode', method='xml')) # thanks copilot

        return BinaryExpression