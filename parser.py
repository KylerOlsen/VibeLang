import ply.yacc as yacc
from lexer import tokens

# AST Node classes
class Node:
    pass

class Program(Node):
    def __init__(self, functions):
        self.functions = functions

class Function(Node):
    def __init__(self, name, body):
        self.name = name
        self.body = body

class Block(Node):
    def __init__(self, statements):
        self.statements = statements

class VariableDeclaration(Node):
    def __init__(self, name, value):
        self.name = name
        self.value = value

class Assignment(Node):
    def __init__(self, name, value):
        self.name = name
        self.value = value

class Print(Node):
    def __init__(self, value):
        self.value = value

class BinaryOp(Node):
    def __init__(self, left, op, right):
        self.left = left
        self.op = op
        self.right = right

class Number(Node):
    def __init__(self, value):
        self.value = value

class Identifier(Node):
    def __init__(self, name):
        self.name = name

# Parser rules
def p_program(p):
    '''program : functions'''
    p[0] = Program(p[1])

def p_functions(p):
    '''functions : function
                 | functions function'''
    if len(p) == 2:
        p[0] = [p[1]]
    else:
        p[0] = p[1] + [p[2]]

def p_function(p):
    '''function : FN IDENTIFIER LPAREN RPAREN LBRACE statements RBRACE'''
    p[0] = Function(p[2], Block(p[6]))

def p_statements(p):
    '''statements : statement
                  | statements statement'''
    if len(p) == 2:
        p[0] = [p[1]]
    else:
        p[0] = p[1] + [p[2]]

def p_statement(p):
    '''statement : variable_declaration
                 | assignment
                 | print_statement
                 | expression SEMICOLON'''
    p[0] = p[1]

def p_variable_declaration(p):
    '''variable_declaration : LET IDENTIFIER ASSIGN expression SEMICOLON'''
    p[0] = VariableDeclaration(p[2], p[4])

def p_assignment(p):
    '''assignment : IDENTIFIER ASSIGN expression SEMICOLON'''
    p[0] = Assignment(p[1], p[3])

def p_print_statement(p):
    '''print_statement : PRINT LPAREN expression RPAREN SEMICOLON'''
    p[0] = Print(p[3])

def p_expression_binop(p):
    '''expression : expression PLUS expression
                  | expression MINUS expression
                  | expression TIMES expression
                  | expression DIVIDE expression
                  | expression EQUALS expression
                  | expression NOTEQUALS expression
                  | expression LESS expression
                  | expression GREATER expression
                  | expression LESSEQUAL expression
                  | expression GREATEREQUAL expression'''
    p[0] = BinaryOp(p[1], p[2], p[3])

def p_expression_group(p):
    '''expression : LPAREN expression RPAREN'''
    p[0] = p[2]

def p_expression_number(p):
    '''expression : NUMBER'''
    p[0] = Number(p[1])

def p_expression_identifier(p):
    '''expression : IDENTIFIER'''
    p[0] = Identifier(p[1])

def p_error(p):
    if p:
        print(f"Syntax error at '{p.value}'")
    else:
        print("Syntax error at EOF")

# Build the parser
parser = yacc.yacc() 