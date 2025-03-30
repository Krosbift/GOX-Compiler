from .helper import Helper
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
        """
        Recupera el siguiente token de la lista de tokens y actualiza el token actual.
        """
        if self.tokens:
            self.current_token = self.tokens.pop(0)
        else:
            self.current_token = None

    def parse(self):
        return self.program()

    def program(self):
        """
        ### statement* EOF
        """
        statements = []
        while self.current_token and self.current_token.type != "EOF":
            statements.append(self.statement())
        return Program(statements)

    def statement(self):
        """
        ### statement <- assignment
        ###           / vardecl
        ###           / funcdecl
        ###           / if_stmt
        ###           / while_stmt
        ###           / break_stmt
        ###           / continue_stmt
        ###           / return_stmt
        ###           / print_stmt
        """
        if self.current_token.type == "ID":
            if Helper.peek_token(self).type == "ASSIGN":
                return self.assignment()
            elif Helper.peek_token(self).type == "LPAREN":
                return self.func_call()
            else:
                Helper.error(f"Unexpected token after ID: {Helper.peek_token(self)}")
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
            Helper.error(f"Unexpected token: {self.current_token}")

    def assignment(self):
        """
        ### location '=' expression ';'
        """
        location = self.location()
        Helper.expect(self, "ASSIGN")
        expression = self.expression()
        Helper.expect(self, "SEMI")
        return Assignment(location, expression)

    def vardecl(self):
        """
        ### ('var' / 'const') ID type? ('=' expression)? ';'
        """
        kind = self.current_token.type
        self.next_token()
        identifier = self.current_token.value
        Helper.expect(self, "ID")
        var_type = None
        if self.current_token.type in ("INT", "FLOAT_TYPE", "CHAR_TYPE", "BOOL"):
            var_type = self.current_token.value
            self.next_token()
        initializer = None
        if self.current_token.type == "ASSIGN":
            self.next_token()
            initializer = self.expression()
        Helper.expect(self, "SEMI")
        return VarDecl(kind, identifier, var_type, initializer)

    def funcdecl(self):
        """
        ### 'import'? 'func' ID '(' parameters ')' type '{' statement* '}'
        """
        is_import = False
        if self.current_token.type == "IMPORT":
            is_import = True
            self.next_token()
        Helper.expect(self, "FUNC")
        identifier = self.current_token.value
        Helper.expect(self, "ID")
        Helper.expect(self, "LPAREN")
        parameters = self.parameters()
        Helper.expect(self, "RPAREN")
        return_type = Helper.expect_type(self)
        Helper.expect(self, "LBRACE")
        body = []
        while self.current_token.type != "RBRACE":
            body.append(self.statement())
        Helper.expect(self, "RBRACE")
        return FuncDecl(is_import, identifier, parameters, return_type, body)

    def if_stmt(self):
        """
        ### 'if' expression '{' statement* '}' ('else' '{' statement* '}')?
        """
        Helper.expect(self, "IF")
        condition = self.expression()
        Helper.expect(self, "LBRACE")
        then_block = []
        while self.current_token.type != "RBRACE":
            then_block.append(self.statement())
        Helper.expect(self, "RBRACE")
        else_block = None
        if self.current_token:
            if self.current_token.type == "ELSE":
                self.next_token()
                Helper.expect(self, "LBRACE")
                else_block = []
                while self.current_token.type != "RBRACE":
                    else_block.append(self.statement())
                Helper.expect(self, "RBRACE")
        return IfStmt(condition, then_block, else_block)

    def while_stmt(self):
        """
        ### 'while' expression '{' statement* '}'
        """
        Helper.expect(self, "WHILE")
        condition = self.expression()
        Helper.expect(self, "LBRACE")
        body = []
        while self.current_token.type != "RBRACE":
            body.append(self.statement())
        Helper.expect(self, "RBRACE")
        return WhileStmt(condition, body)

    def break_stmt(self):
        """
        ### 'break' ';'
        """
        Helper.expect(self, "BREAK")
        Helper.expect(self, "SEMI")
        return BreakStmt()

    def continue_stmt(self):
        """
        ### 'continue' ';'
        """
        Helper.expect(self, "CONTINUE")
        Helper.expect(self, "SEMI")
        return ContinueStmt()

    def return_stmt(self):
        """
        ### 'return' expression ';'
        """
        Helper.expect(self, "RETURN")
        expression = self.expression()
        Helper.expect(self, "SEMI")
        return ReturnStmt(expression)

    def print_stmt(self):
        """
        ### 'print' expression ';'
        """
        Helper.expect(self, "PRINT")
        expression = self.expression()
        Helper.expect(self, "SEMI")
        return PrintStmt(expression)

    def parameters(self):
        """
        ### ID type (',' ID type)* / empty
        """
        params = []
        if self.current_token.type != "RPAREN":
            param_name = self.current_token.value
            Helper.expect(self, "ID")
            param_type = Helper.expect_type(self)
            params.append((param_name, param_type))
            while self.current_token.type == "COMMA":
                self.next_token()
                param_name = self.current_token.value
                Helper.expect(self, "ID")
                param_type = Helper.expect_type(self)
                params.append((param_name, param_type))
        return Parameters(params)

    def expression(self):
        return self.orterm()

    def orterm(self):
        """
        ### expression ('||') expression
        """
        node = self.andterm()
        while self.current_token.type == "LOR":
            op = self.current_token.value
            self.next_token()
            node = BinaryOp(node, op, self.andterm())
        return node

    def andterm(self):
        """
        ### expression ('&&') expression
        """
        node = self.relterm()
        while self.current_token.type == "LAND":
            op = self.current_token.value
            self.next_token()
            node = BinaryOp(node, op, self.relterm())
        return node

    def relterm(self):
        """
        ### expression ('<' / '>' / '<=' / '>=' / '==' / '!=') expression
        """
        node = self.addterm()
        while self.current_token.type in ("LT", "GT", "LE", "GE", "EQ", "NE"):
            op = self.current_token.value
            self.next_token()
            node = BinaryOp(node, op, self.addterm())
        return node

    def addterm(self):
        """
        ### expression ('+' / '-') expression
        """
        node = self.factor()
        while self.current_token.type in ("PLUS", "MINUS"):
            op = self.current_token.value
            self.next_token()
            node = BinaryOp(node, op, self.factor())
        return node

    def factor(self):
        """
        ### expression ('*' / '/') expression
        """
        node = self.primary()
        while self.current_token.type in ("TIMES", "DIVIDE"):
            op = self.current_token.value
            self.next_token()
            node = BinaryOp(node, op, self.primary())
        return node

    def primary(self):
        """
        ### ('+' / '-' / '^') expression |
        ### INTEGER / FLOAT / CHAR / bool |
        ### type '(' expression ')' |
        ### 'int' / 'float' / 'char' / 'bool' |
        """
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
            Helper.expect(self, "RPAREN")
            return expr
        elif token.type in ("INT", "FLOAT_TYPE", "CHAR_TYPE", "BOOL"):
            cast_type = token.value
            self.next_token()
            Helper.expect(self, "LPAREN")
            expr = self.expression()
            Helper.expect(self, "RPAREN")
            return Cast(cast_type, expr)
        elif token.type == "ID":
            name = token.value
            self.next_token()
            if self.current_token.type == "LPAREN":
                self.next_token()
                args = self.arguments()
                Helper.expect(self, "RPAREN")
                return FunctionCall(name, args)
            else:
                return IdentifierLocation(name)
        elif token.type == "DEREF":
            self.next_token()
            expr = self.expression()
            return DereferenceLocation(expr)
        else:
            Helper.error(f"Unexpected token in primary: {token}")

    def arguments(self):
        args = []
        if self.current_token.type != "RPAREN":
            args.append(self.expression())
            while self.current_token.type == "COMMA":
                self.next_token()
                args.append(self.expression())
        return args

    def location(self):
        """
        ### ID | '`' expression
        """
        if self.current_token.type == "ID":
            name = self.current_token.value
            self.next_token()
            return IdentifierLocation(name)
        elif self.current_token.type == "DEREF":
            self.next_token()
            expr = self.expression()
            return DereferenceLocation(expr)
        else:
            Helper.error(f"Unexpected token in location: {self.current_token}")

    def func_call(self):
        """
        ### ID '(' arguments ')'
        """
        name = self.current_token.value
        self.next_token()
        Helper.expect(self, "LPAREN")
        args = self.arguments()
        Helper.expect(self, "RPAREN")
        Helper.expect(self, "SEMI")
        return FunctionCall(name, args)
