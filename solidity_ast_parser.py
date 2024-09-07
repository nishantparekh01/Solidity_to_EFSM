# Ignored nodeTypes :
# 1. IdentifierPath

from efsm_framework import *
import xml.etree.ElementTree as ET
from wmodify import *

def ntype(node):
    return node['nodeType']

def handleMemberAccess(node):
    assert ntype(node) == 'MemberAccess', "Node not MemberAccess"
    memberName = node['memberName']
    name = lookup_table[ntype(node['expression'])](node['expression']) # name = {'ntype': 'FunctionCall', 'name' : name, 'args' : 'msg.sender'}
    #name = node['expression']['name']
    if isinstance(name, dict):
        return name['args'] + "." + memberName
        # example:
        #return memberName
    else:
        #return str(name + '.' + memberName)
        if memberName == 'transfer':
            return {'name':name + memberName , 'type': 'transfer'}
        else:
            return memberName
        # example :

def handleIdentifier(node):
    assert ntype(node) == 'Identifier', "Node not Identifier"
    name = node['name']
    return name

def handleVariableDeclaration(node):
    assert ntype(node) == 'VariableDeclaration', " Node not VariableDeclaration"
    name = node['name']
    var_type = lookup_table[ntype(node['typeName'])](node['typeName'])
    #return str(var_type + " : " + name)
    packet = {'name': name, 'type': var_type}

    if superVariableDeclaration(packet):
        return  True
    return(name)

def handleElementaryTypeName(node):
    assert ntype(node) == 'ElementaryTypeName', "Node not ElementaryTypeName"
    name = node['name']
    return name

def handleUserDefinedTypeName(node):
    assert ntype(node) == 'UserDefinedTypeName', "Node not UserDefinedTypeName"
    name = node['pathNode']['name']
    return name

def handleEnumValue(node):
    assert ntype(node) == 'EnumValue', "Node not EnumValue"
    name = node['name']
    return  name

def handleEnumDefinition(node):
    assert ntype(node) == 'EnumDefinition', "Node not EnumDefinition"
    name = node['name']
    members = []
    for m_node in node['members']:
        m_name = lookup_table[ntype(m_node)](m_node)
        members.append(m_name)
    packet = {'name': name, 'members': members}
    superEnumDefinition(packet)
    #return str ( name + " : " + str(members))


def handleIdentifier(node):
    assert ntype(node) == 'Identifier', "Node not Identifier"
    name = node['name']
    return name

def handleBinaryOperation(node):
    assert ntype(node) == 'BinaryOperation', "Node not BinaryOperation"
    lhs = lookup_table[ntype(node['leftExpression'])](node['leftExpression'])
    op = node['operator']
    rhs = lookup_table[ntype(node['rightExpression'])](node['rightExpression'])

    # if op == "||" then convert to "|" and similarly if op == "&&" then convert to "&"
    if op == "||":
        op = "|"
    elif op == "&&":
        op = "&"

    #exp = str(lhs + " "  + op + " " + rhs)
    exp = wmodify_assignment(lhs, op, rhs)
    # if isinstance(exp, ET.Element):
    #     return str(ET.tostring(exp, encoding='utf-8', method='xml').decode('utf-8'))
    # else:
    #     return exp
    return exp


    # if isinstance(rhs, dict):
    #     return str(lhs + " "  + op + " " + str(rhs['name'] + "(" + rhs['args'] + ")"))
    # else:
    #     return exp
    #return exp

def handleFunctionCall(node):
    assert ntype(node) == 'FunctionCall', "Node not FunctionCall"
    name = lookup_table[ntype(node['expression'])](node['expression'])
    if name == 'keccak256':
        arg = node['arguments'][0]['arguments'][0]['name']
    else:
        if len(node['arguments']) == 0:
            arg = ""
        else:
            arg_list = []
            for a in node['arguments']:
                arg = lookup_table[ntype(a)](a)
                # if isinstance(arg, dict):
                #     arg_list.append(str(arg['name'] + "(" + arg['args'] + ")"))
                # else:
                #     arg_list.append(arg) # msg.sender
            # if argument is a dictionary then convert the dictionary into string with function call
            #print("arg_list here", arg_list)
            #args  = ' '.join(arg_list)
            #print(ET.tostring(arg, encoding='utf-8', method='xml').decode('utf-8'))

    if isinstance(name, dict):
        return {'ntype': ntype(node), 'name' : name['name'], 'args' : arg, 'type': name['type']}
    else:
        return {'ntype': ntype(node), 'name' : name, 'args' : arg} # args value : msg.sender


def handleExpressionStatement(node):
    assert ntype(node) == 'ExpressionStatement', "Node not ExpressionStatement"
    exp = lookup_table[ntype(node['expression'])](node['expression'])
    return exp

def handlePlaceholderStatement(node):
    assert ntype(node) == 'PlaceholderStatement', "Node not PlaceholderStatement"
    return False

def handleBlock(node):
    assert ntype(node) == 'Block', "Node not Block"
    statements = []
    for s in node['statements']:
        stmnt = lookup_table[ntype(s)](s)
        statements.append(stmnt)
    return  statements

def handleParameterList(node):
    assert ntype(node) == 'ParameterList', "Node not ParameterList"
    parameters = []
    for p in node['parameters']:
        param = lookup_table[ntype(p)](p)
        parameters.append(param)
    # need to return the parameters as a list
    #params = ', '.join(parameters)
    return parameters

def handleModifierDefinition(node):
    assert ntype(node) == 'ModifierDefinition', "Node not ModifierDefinition"
    packet = {}
    packet['body'] = lookup_table[ntype(node['body'])](node['body'])
    #body = "\n".join(body)
    packet['params'] = lookup_table[ntype(node['parameters'])](node['parameters'])
    packet['name'] = node['name']
    super_struct = superModifierDefinition(packet)
    return super_struct


    #return (name + "(" + params + ")" + "{" + "\n" + body + " " + "\n" + "}")

def handleFunctionDefinition(node):
    assert ntype(node) == 'FunctionDefinition', "Node not FunctionDefinition"
    packet = {}
    packet['body'] = lookup_table[ntype(node['body'])](node['body'])
    packet['params'] = lookup_table[ntype(node['parameters'])](node['parameters'])
    packet['name'] = node['name']
    if packet['name'] == "":
        # do nothing
        return
    packet['modifiers'] = [lookup_table[ntype(m)](m) for m in node['modifiers']]
    super_struct = superFunctionDefinition(packet)
    return super_struct

def handleAssignment(node):
    assert ntype(node) == 'Assignment', "Node not Assignment"
    lhs = lookup_table[ntype(node['leftHandSide'])](node['leftHandSide'])
    op = node['operator']
    rhs = lookup_table[ntype(node['rightHandSide'])](node['rightHandSide'])
    kind = 'simple'

    if isinstance(rhs, dict):
        if rhs['ntype'] == 'FunctionCall':
            #rhs = str(rhs['name'] + "(" + rhs['args'] + ")")
            #exp = str(lhs + " " +op + " " + rhs['name'] + "(" + rhs['args'] + ")")
            exp = wmodify_assignment(lhs, op, rhs)
        elif rhs['ntype'] == 'Conditional':
            kind = 'conditional'
            return {'ntype': ntype(node), 'kind' : kind, 'lhs' : lhs, 'op' : op, 'condition' : rhs['condition'], 'true_exp' : rhs['true_exp'], 'false_exp' : rhs['false_exp']}
    elif isinstance(rhs, ET.Element) or isinstance(rhs, str):
        exp = wmodify_assignment(lhs, op, rhs)
    #exp = wmodify_assignment(lhs, op, rhs)
    return  {'ntype': ntype(node), 'kind' : kind, 'exp' : exp}

def handleModifierInvocation(node):
    assert ntype(node) == 'ModifierInvocation', "Node not ModifierInvocation"
    name = lookup_table[ntype(node['modifierName'])](node['modifierName'])
    if 'arguments' in node:
        args = [lookup_table[ntype(a)](a) for a in node['arguments']]
        return {'name':name, 'args': args}
    else:
        return {'name':name}

def handleIdentifierPath(node):
    assert ntype(node) == 'IdentifierPath', "Node not IdentifierPath"
    name = node['name']
    return name

def handleLiteral(node):
    assert ntype(node) == 'Literal', "Node not Literal"
    value = node['value']
    return value

def handleElementaryTypeNameExpression(node):
    assert ntype(node) == 'ElementaryTypeNameExpression', "Node not ElementaryTypeNameExpression"
    return ""

def handleVariableDeclarationStatement(node):
    assert ntype(node) == 'VariableDeclarationStatement', "Node not VariableDeclarationStatement"

    # assumption - there is only one variable declaration here
    #name = "".join([lookup_table[ntype(d)](d) for d in node['declarations']])
    name = lookup_table[ntype(node['declarations'][0])](node['declarations'][0])
    init_value = lookup_table[ntype(node['initialValue'])](node['initialValue'])
    if isinstance(init_value, dict):
        if init_value['ntype'] == 'Conditional':

            exp = wmodify_assignment(name,"==", init_value['true_exp'], **{'ntype': ntype(node), 'kind': 'conditional', 'name' : name, 'condition': init_value['condition'], 'true_exp': init_value['true_exp'], 'false_exp': init_value['false_exp']})


            return {'ntype': ntype(node), 'kind' : 'conditional', 'expression' : exp}
    else:
        return str (name + " = " + init_value)  # need to convert this to xml as well. For later.

def handleConditional(node):
    assert ntype(node) == 'Conditional', "Node not conditional"
    condition = lookup_table[ntype(node['condition'])](node['condition'])
    false_exp = lookup_table[ntype(node['falseExpression'])](node['falseExpression'])
    true_exp = lookup_table[ntype(node['trueExpression'])](node['trueExpression'])
    #return  str("(" + condition + ")" + "? " + true_exp + " : " + false_exp + ";")
    return {'ntype': ntype(node), 'condition' : condition, 'true_exp' : true_exp, 'false_exp' : false_exp}


def handleTupleExpression(node):
    assert ntype(node)  == 'TupleExpression', "Node not TupleExpression"
        # assumption - there is only expression here
    comp = lookup_table[ntype(node['components'][0])](node['components'][0])
    return comp

def handleIfStatement(node):
    assert ntype(node) == 'IfStatement', "Node not IfStatement"
    true_condition = lookup_table[ntype(node['condition'])](node['condition'])
    false_condition = ET.Element("UnaryExpression", Operator = "!")
    false_condition.append(true_condition)

    false_body = lookup_table[ntype(node['falseBody'])](node['falseBody'])
    #print(false_body)
    true_body = lookup_table[ntype(node['trueBody'])](node['trueBody'])
    #print(true_body)
    #return  str("if" + "( " + condition+" )" + "{\n\t"  + true_body + "\n" + "} " + "else "  + "{\n\t" + false_body + "\n" + "} ")
    return {'ntype': ntype(node), 'true_condition' : true_condition,'false_condition': false_condition, 'true_body' : true_body, 'false_body' : false_body}


def handleStructDefinition(node):
    assert ntype(node) == 'StructDefinition', "Node not StructDefinition"
    members = [lookup_table[ntype(m)](m) for m in node['members']]
    #members = "\n".join(members)
    name = node['name']
    packet = {'name': name, 'members': members}
    if superStructDefinition(packet):
        return True
    #return str (name + " {\n" + members + "\n}")

def handleMapping(node):
    assert ntype(node) == 'Mapping', "Node not Mapping"
    key = lookup_table[ntype(node['keyType'])](node['keyType'])
    value = lookup_table[ntype(node['valueType'])](node['valueType'])
    return  str( key + " => "  + value)

def handleIndexAccess(node):
    assert ntype(node) == 'IndexAccess' , "Node not IndexAccess"
    base = lookup_table[ntype(node['baseExpression'])](node['baseExpression'])
    index = lookup_table[ntype(node['indexExpression'])](node['indexExpression'])
    return  str( base + "[" + index + "]")

def structConstructorCall(node):
    assert ntype(node) == 'StructConstructorCall', "Node not StructConstructorCall"



lookup_table = {}

lookup_table['MemberAccess'] = handleMemberAccess
lookup_table['Identifier'] = handleIdentifier
lookup_table['BinaryOperation'] = handleBinaryOperation
lookup_table['ElementaryTypeName'] = handleElementaryTypeName
lookup_table['VariableDeclaration'] = handleVariableDeclaration
lookup_table['UserDefinedTypeName'] = handleUserDefinedTypeName
lookup_table['EnumValue'] = handleEnumValue
lookup_table['EnumDefinition'] = handleEnumDefinition
lookup_table['Identifier'] = handleIdentifier
lookup_table['FunctionCall'] = handleFunctionCall
lookup_table['ExpressionStatement'] = handleExpressionStatement
lookup_table['PlaceholderStatement'] = handlePlaceholderStatement
lookup_table['Block'] = handleBlock
lookup_table['ModifierDefinition'] = handleModifierDefinition
lookup_table['ParameterList'] = handleParameterList
lookup_table['FunctionDefinition'] = handleFunctionDefinition
lookup_table['Assignment'] = handleAssignment
lookup_table['ModifierInvocation'] = handleModifierInvocation
lookup_table['IdentifierPath'] = handleIdentifierPath
lookup_table['Literal'] = handleLiteral
lookup_table['ElementaryTypeNameExpression'] = handleElementaryTypeNameExpression
lookup_table['VariableDeclarationStatement'] = handleVariableDeclarationStatement
lookup_table['Conditional'] = handleConditional
lookup_table['TupleExpression'] = handleTupleExpression
lookup_table['IfStatement'] = handleIfStatement
lookup_table['StructDefinition'] = handleStructDefinition
lookup_table['Mapping'] = handleMapping
lookup_table['IndexAccess'] = handleIndexAccess


