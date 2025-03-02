import re

# Definición de los tokens
TOKEN_REGEX = {
    'NUMBER': r'\d+',
    'IDENTIFIER': r'[a-zA-Z_]\w*',
    'ASSIGN': r'=',
    'PLUS': r'\+',
    'MINUS': r'-',
    'TIMES': r'\*',
    'DIVIDE': r'/',
    'SEMICOLON': r';',
    'LPAREN': r'\(',
    'RPAREN': r'\)',
}

# Lexer
class Lexer:
    def __init__(self, code):
        self.tokens = self.tokenize(code)
        self.pos = 0

    def tokenize(self, code):
        pattern = '|'.join(f'(?P<{name}>{regex})' for name, regex in TOKEN_REGEX.items())
        tokens = []
        for match in re.finditer(pattern, code):
            for name, value in match.groupdict().items():
                if value is not None:
                    tokens.append((name, value))
        return tokens

    def next_token(self):
        if self.pos < len(self.tokens):
            token = self.tokens[self.pos]
            self.pos += 1
            return token
        return ('EOF', '')

    def peek(self):
        if self.pos < len(self.tokens):
            return self.tokens[self.pos]
        return ('EOF', '')

# Nodos del AST
class Node:
    pass

class Program(Node):
    def __init__(self, statements):
        self.statements = statements

class Expression(Node):
    def __init__(self, value):
        self.value = value

class Assignment(Node):
    def __init__(self, identifier, expression):
        self.identifier = identifier
        self.expression = expression

class BinaryOperation(Node):
    def __init__(self, left, operator, right):
        self.left = left
        self.operator = operator
        self.right = right

class Number(Node):
    def __init__(self, value):
        self.value = value

class Identifier(Node):
    def __init__(self, name):
        self.name = name

# Parser
class Parser:
    def __init__(self, lexer):
        self.lexer = lexer
        self.current_token = self.lexer.next_token()

    def eat(self, token_type):
        if self.current_token[0] == token_type:
            self.current_token = self.lexer.next_token()
        else:
            raise SyntaxError(f'Expected {token_type} but got {self.current_token[0]}')

    def parse(self):
        statements = []
        while self.current_token[0] != 'EOF':
            statements.append(self.parse_statement())
        return Program(statements)

    def parse_statement(self):
        if self.current_token[0] == 'IDENTIFIER' and self.lexer.peek()[0] == 'ASSIGN':
            return self.parse_assignment()
        else:
            expr = self.parse_expression()
            self.eat('SEMICOLON')
            return Expression(expr)

    def parse_assignment(self):
        identifier = Identifier(self.current_token[1])
        self.eat('IDENTIFIER')
        self.eat('ASSIGN')
        expr = self.parse_expression()
        self.eat('SEMICOLON')
        return Assignment(identifier, expr)

    def parse_expression(self):
        node = self.parse_term()
        while self.current_token[0] in ('PLUS', 'MINUS'):
            operator = self.current_token[1]
            self.eat(self.current_token[0])
            node = BinaryOperation(node, operator, self.parse_term())
        return node

    def parse_term(self):
        node = self.parse_factor()
        while self.current_token[0] in ('TIMES', 'DIVIDE'):
            operator = self.current_token[1]
            self.eat(self.current_token[0])
            node = BinaryOperation(node, operator, self.parse_factor())
        return node

    def parse_factor(self):
        token = self.current_token
        if token[0] == 'NUMBER':
            self.eat('NUMBER')
            return Number(int(token[1]))
        elif token[0] == 'IDENTIFIER':
            self.eat('IDENTIFIER')
            return Identifier(token[1])
        elif token[0] == 'LPAREN':
            self.eat('LPAREN')
            node = self.parse_expression()
            self.eat('RPAREN')
            return node
        elif token[0] == 'MINUS':
            self.eat('MINUS')
            return BinaryOperation(Number(0), '-', self.parse_factor())
        else:
            raise SyntaxError(f'Unexpected token: {token}')

# Prueba
code = """
    a = 1 + 2 * 3 / 4 - 5;
    a * 78;
    b = 14 / 35;
    - (a * b);
"""
lexer = Lexer(code)
parser = Parser(lexer)
ast = parser.parse()

# Función para imprimir el AST
import json

def ast_to_dict(node):
    if isinstance(node, Program):
        return {'Program': [ast_to_dict(stmt) for stmt in node.statements]}
    elif isinstance(node, Assignment):
        return {'Assignment': {'identifier': node.identifier.name, 'expression': ast_to_dict(node.expression)}}
    elif isinstance(node, Expression):
        return {'Expression': ast_to_dict(node.value)}
    elif isinstance(node, BinaryOperation):
        return {'BinaryOperation': {'left': ast_to_dict(node.left), 'operator': node.operator, 'right': ast_to_dict(node.right)}}
    elif isinstance(node, Number):
        return {'Number': node.value}
    elif isinstance(node, Identifier):
        return {'Identifier': node.name}
    return 'Unknown Node'

print(json.dumps(ast_to_dict(ast), indent=4))
