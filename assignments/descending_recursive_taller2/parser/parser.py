from .AST.grammar.program import Program
from .AST.grammar.assignment import Assignment
from .AST.grammar.expression import Expression
from .AST.grammar.binary_operation import BinaryOperation
from .AST.grammar.number import Number
from .AST.grammar.identifier import Identifier


class Parser:
    def __init__(self, lexer):
        self.lexer = lexer
        self.current_token = self.lexer.next_token()

    def eat(self, token_type):
        if self.current_token[0] == token_type:
            self.current_token = self.lexer.next_token()
        else:
            raise SyntaxError(f"Expected {token_type} but got {self.current_token[0]}")

    def parse(self):
        statements = []
        while self.current_token[0] != "EOF":
            statements.append(self.parse_statement())
        return Program(statements)

    def parse_statement(self):
        if self.current_token[0] == "IDENTIFIER" and self.lexer.peek()[0] == "ASSIGN":
            return self.parse_assignment()
        else:
            expr = self.parse_expression()
            self.eat("SEMICOLON")
            return Expression(expr)

    def parse_assignment(self):
        identifier = Identifier(self.current_token[1])
        self.eat("IDENTIFIER")
        self.eat("ASSIGN")
        expr = self.parse_expression()
        self.eat("SEMICOLON")
        return Assignment(identifier, expr)

    def parse_expression(self):
        node = self.parse_term()
        while self.current_token[0] in ("PLUS", "MINUS"):
            operator = self.current_token[1]
            self.eat(self.current_token[0])
            node = BinaryOperation(node, operator, self.parse_term())
        return node

    def parse_term(self):
        node = self.parse_factor()
        while self.current_token[0] in ("TIMES", "DIVIDE"):
            operator = self.current_token[1]
            self.eat(self.current_token[0])
            node = BinaryOperation(node, operator, self.parse_factor())
        return node

    def parse_factor(self):
        token = self.current_token
        if token[0] == "NUMBER":
            self.eat("NUMBER")
            return Number(int(token[1]))
        elif token[0] == "IDENTIFIER":
            self.eat("IDENTIFIER")
            return Identifier(token[1])
        elif token[0] == "LPAREN":
            self.eat("LPAREN")
            node = self.parse_expression()
            self.eat("RPAREN")
            return node
        elif token[0] == "MINUS":
            self.eat("MINUS")
            return BinaryOperation(Number(0), "-", self.parse_factor())
        else:
            raise SyntaxError(f"Unexpected token: {token}")
