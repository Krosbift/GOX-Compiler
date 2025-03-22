from .AST.grammar.program import Program
from .AST.grammar.assigment import Assignment
from .AST.grammar.vardecl import VarDecl
from .AST.grammar.funcdecl import FuncDecl
from .AST.grammar.if_stmt import IfStmt
from .AST.grammar.while_stmt import WhileStmt
from .AST.grammar.break_stmt import BreakStmt
from .AST.grammar.continue_stmt import ContinueStmt
from .AST.grammar.return_stmt import ReturnStmt
from .AST.grammar.print_stmt import PrintStmt
from .AST.grammar.parameters import Parameters
from .AST.grammar.binary_operator import BinaryOp
from .AST.grammar.unary_operator import UnaryOp
from .AST.grammar.literal import Literal
from .AST.grammar.identifier_location import IdentifierLocation
from .AST.grammar.dereference_location import DereferenceLocation
from .AST.grammar.function_call import FunctionCall
from .AST.grammar.cast import Cast

class Parser:
    def __init__(self, tokens):
        self.tokens = tokens
        self.current_token = None
        self.next_token()

    def next_token(self):
        if self.tokens:
            self.current_token = self.tokens.pop(0)
        else:
            self.current_token = None

    def parse(self):
        return self.program()

    def program(self):
        statements = []
        while self.current_token and self.current_token.type != "EOF":
            statements.append(self.statement())
        return Program(statements)

    def statement(self):
        if self.current_token.type == "ID":
            if self.peek_token().type == "ASSIGN":
                return self.assignment()
            elif self.peek_token().type == "LPAREN":
                return self.func_call()
            else:
                self.error(f"Unexpected token after ID: {self.peek_token()}")
        elif self.current_token.type in ("VAR", "CONST"):
            return self.vardecl()
        elif self.current_token.type == "FUNC":
            return self.funcdecl()
        elif self.current_token.type == "IF":
            return self.if_stmt()
        elif self.current_token.type == "WHILE":
            return self.while_stmt()
        elif self.current_token.type == "BREAK":
            return self.break_stmt()
        elif self.current_token.type == "CONTINUE":
            return self.continue_stmt()
        elif self.current_token.type == "RETURN":
            return self.return_stmt()
        elif self.current_token.type == "PRINT":
            return self.print_stmt()
        else:
            self.error(f"Unexpected token: {self.current_token}")

    def assignment(self):
        location = self.location()
        self.expect("ASSIGN")
        expression = self.expression()
        self.expect("SEMI")
        return Assignment(location, expression)

    def vardecl(self):
        kind = self.current_token.type
        self.next_token()
        identifier = self.current_token.value
        self.expect("ID")
        var_type = None
        if self.current_token.type in ("INT", "FLOAT_TYPE", "CHAR_TYPE", "BOOL"):
            var_type = self.current_token.value
            self.next_token()
        initializer = None
        if self.current_token.type == "ASSIGN":
            self.next_token()
            initializer = self.expression()
        self.expect("SEMI")
        return VarDecl(kind, identifier, var_type, initializer)

    def funcdecl(self):
        is_import = False
        if self.current_token.type == "IMPORT":
            is_import = True
            self.next_token()
        self.expect("FUNC")
        identifier = self.current_token.value
        self.expect("ID")
        self.expect("LPAREN")
        parameters = self.parameters()
        self.expect("RPAREN")
        return_type = self.expect_type()
        self.expect("LBRACE")
        body = []
        while self.current_token.type != "RBRACE":
            body.append(self.statement())
        self.expect("RBRACE")
        return FuncDecl(is_import, identifier, parameters, return_type, body)

    def if_stmt(self):
        self.expect("IF")
        condition = self.expression()
        self.expect("LBRACE")
        then_block = []
        while self.current_token.type != "RBRACE":
            then_block.append(self.statement())
        self.expect("RBRACE")
        else_block = None
        if self.current_token.type == "ELSE":
            self.next_token()
            self.expect("LBRACE")
            else_block = []
            while self.current_token.type != "RBRACE":
                else_block.append(self.statement())
            self.expect("RBRACE")
        return IfStmt(condition, then_block, else_block)

    def while_stmt(self):
        self.expect("WHILE")
        condition = self.expression()
        self.expect("LBRACE")
        body = []
        while self.current_token.type != "RBRACE":
            body.append(self.statement())
        self.expect("RBRACE")
        return WhileStmt(condition, body)

    def break_stmt(self):
        self.expect("BREAK")
        self.expect("SEMI")
        return BreakStmt()

    def continue_stmt(self):
        self.expect("CONTINUE")
        self.expect("SEMI")
        return ContinueStmt()

    def return_stmt(self):
        self.expect("RETURN")
        expression = self.expression()
        self.expect("SEMI")
        return ReturnStmt(expression)

    def print_stmt(self):
        self.expect("PRINT")
        expression = self.expression()
        self.expect("SEMI")
        return PrintStmt(expression)

    def parameters(self):
        params = []
        if self.current_token.type != "RPAREN":
            param_name = self.current_token.value
            self.expect("ID")
            param_type = self.expect_type()
            params.append((param_name, param_type))
            while self.current_token.type == "COMMA":
                self.next_token()
                param_name = self.current_token.value
                self.expect("ID")
                param_type = self.expect_type()
                params.append((param_name, param_type))
        return Parameters(params)

    def expression(self):
        return self.orterm()

    def orterm(self):
        node = self.andterm()
        while self.current_token.type == "LOR":
            op = self.current_token.value
            self.next_token()
            node = BinaryOp(node, op, self.andterm())
        return node

    def andterm(self):
        node = self.relterm()
        while self.current_token.type == "LAND":
            op = self.current_token.value
            self.next_token()
            node = BinaryOp(node, op, self.relterm())
        return node

    def relterm(self):
        node = self.addterm()
        while self.current_token.type in ("LT", "GT", "LE", "GE", "EQ", "NE"):
            op = self.current_token.value
            self.next_token()
            node = BinaryOp(node, op, self.addterm())
        return node

    def addterm(self):
        node = self.factor()
        while self.current_token.type in ("PLUS", "MINUS"):
            op = self.current_token.value
            self.next_token()
            node = BinaryOp(node, op, self.factor())
        return node

    def factor(self):
        node = self.primary()
        while self.current_token.type in ("TIMES", "DIVIDE"):
            op = self.current_token.value
            self.next_token()
            node = BinaryOp(node, op, self.primary())
        return node

    def primary(self):
        token = self.current_token
        if token.type in ("INTEGER", "FLOAT", "CHAR", "TRUE", "FALSE"):
            self.next_token()
            return Literal(token.value, token.type)
        elif token.type in ("PLUS", "MINUS", "GROW"):
            self.next_token()
            return UnaryOp(token.value, self.expression())
        elif token.type == "LPAREN":
            self.next_token()
            expr = self.expression()
            self.expect("RPAREN")
            return expr
        elif token.type in ("INT", "FLOAT_TYPE", "CHAR_TYPE", "BOOL"):
            cast_type = token.value
            self.next_token()
            self.expect("LPAREN")
            expr = self.expression()
            self.expect("RPAREN")
            return Cast(cast_type, expr)
        elif token.type == "ID":
            name = token.value
            self.next_token()
            if self.current_token.type == "LPAREN":
                self.next_token()
                args = self.arguments()
                self.expect("RPAREN")
                return FunctionCall(name, args)
            else:
                return IdentifierLocation(name)
        elif token.type == "DEREF":
            self.next_token()
            expr = self.expression()
            return DereferenceLocation(expr)
        else:
            self.error(f"Unexpected token in primary: {token}")

    def arguments(self):
        args = []
        if self.current_token.type != "RPAREN":
            args.append(self.expression())
            while self.current_token.type == "COMMA":
                self.next_token()
                args.append(self.expression())
        return args

    def location(self):
        if self.current_token.type == "ID":
            name = self.current_token.value
            self.next_token()
            return IdentifierLocation(name)
        elif self.current_token.type == "DEREF":
            self.next_token()
            expr = self.expression()
            return DereferenceLocation(expr)
        else:
            self.error(f"Unexpected token in location: {self.current_token}")

    def expect(self, token_type):
        if self.current_token.type == token_type:
            value = self.current_token.value
            self.next_token()
            return value
        else:
            self.error(f"Expected token {token_type}, but got {self.current_token}")

    def expect_type(self):
        if self.current_token.type in ("INT", "FLOAT_TYPE", "CHAR_TYPE", "BOOL"):
            value = self.current_token.value
            self.next_token()
            return value
        else:
            self.error(f"Expected type token, but got {self.current_token}")

    def error(self, message):
        raise SyntaxError(message)

    def peek_token(self):
        if self.tokens:
            return self.tokens[0]
        else:
            return None

    def func_call(self):
        name = self.current_token.value
        self.next_token()
        self.expect("LPAREN")
        args = self.arguments()
        self.expect("RPAREN")
        self.expect("SEMI")
        return FunctionCall(name, args)