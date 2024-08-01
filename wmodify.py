# importing modules
import xml.etree.ElementTree as ET


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



    else:
        if isinstance(rhs, dict) and isinstance(lhs, str):

            BinaryExpression = ET.Element("BinaryExpression", Operator = str(op))
            SimpleIdentifier = ET.SubElement(BinaryExpression, "SimpleIdentifier", Name = str(lhs))
            SimpleIdentifier = ET.SubElement(BinaryExpression, "SimpleIdentifier", Name = str(rhs['args']))


            #print(rhs['args'])
            #print(rhs['name'])
            #rhs = str(lhs + " "  + op + " " + str(rhs['name'] + "(" + rhs['args'] + ")"))


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
            #print('-------------------xml party here--------------------------')
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
            #print('-------------------lhs:xml, rhs:str --------------------------')
            #print(ET.tostring(BinaryExpression, encoding='unicode', method='xml'))
            #return str(ET.tostring(BinaryExpression, encoding='unicode', method='xml'))
            return BinaryExpression

        # Convert this to a string and return
        #print(ET.tostring(BinaryExpression))
        #print(type(BinaryExpression))

        #print(str(ET.tostring(BinaryExpression, encoding='unicode', method='xml')))
        #return str(ET.tostring(BinaryExpression, encoding='unicode', method='xml')) # thanks copilot

        return BinaryExpression