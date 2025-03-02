from ..lexical_analyzer.tokens.gox_tokens import Token

class ASTNode:
    pass


class Program(ASTNode):
    def __init__(self, statements):
        self.statements = statements


class Assignment(ASTNode):
    def __init__(self, location, expression):
        self.location = location
        self.expression = expression


class VarDecl(ASTNode):
    def __init__(self, kind, identifier, var_type, initializer):
        self.kind = kind
        self.identifier = identifier
        self.var_type = var_type
        self.initializer = initializer


class FuncDecl(ASTNode):
    def __init__(self, is_import, name, parameters, return_type, body):
        self.is_import = is_import
        self.name = name
        self.parameters = parameters
        self.return_type = return_type
        self.body = body


class IfStmt(ASTNode):
    def __init__(self, condition, then_block, else_block):
        self.condition = condition
        self.then_block = then_block
        self.else_block = else_block


class WhileStmt(ASTNode):
    def __init__(self, condition, body):
        self.condition = condition
        self.body = body


class BreakStmt(ASTNode):
    pass


class ContinueStmt(ASTNode):
    pass


class ReturnStmt(ASTNode):
    def __init__(self, expression):
        self.expression = expression


class PrintStmt(ASTNode):
    def __init__(self, expression):
        self.expression = expression


class Parameters(ASTNode):
    def __init__(self, params):
        self.params = params


class Type(ASTNode):
    def __init__(self, name):
        self.name = name


class IdentifierLocation(ASTNode):
    def __init__(self, name):
        self.name = name


class DereferenceLocation(ASTNode):
    def __init__(self, expression):
        self.expression = expression


class BinaryOp(ASTNode):
    def __init__(self, left, op, right):
        self.left = left
        self.op = op
        self.right = right


class UnaryOp(ASTNode):
    def __init__(self, op, expr):
        self.op = op
        self.expr = expr


class Literal(ASTNode):
    def __init__(self, value, type_token):
        self.value = value
        self.type_token = type_token


class Cast(ASTNode):
    def __init__(self, cast_type, expression):
        self.cast_type = cast_type
        self.expression = expression


class FunctionCall(ASTNode):
    def __init__(self, name, arguments):
        self.name = name
        self.arguments = arguments
















class Parser:
    def __init__(self, tokens):
        self.tokens = tokens
        self.pos = 0
        self.current_token = tokens[0] if tokens else None

    def consume(self, expected_type=None):
        if self.current_token is None:
            raise SyntaxError("Unexpected end of input")
        if expected_type is not None and self.current_token.type != expected_type:
            raise SyntaxError(
                f"Expected {expected_type}, got {self.current_token.type} at line {self.current_token.line}, column {self.current_token.column}"
            )
        token = self.current_token
        self.pos += 1
        if self.pos < len(self.tokens):
            self.current_token = self.tokens[self.pos]
        else:
            self.current_token = Token("EOF", "", token.line, token.column + 1)
        return token

    def peek(self):
        if self.pos + 1 < len(self.tokens):
            return self.tokens[self.pos + 1]
        else:
            return Token(
                "EOF", "", self.current_token.line, self.current_token.column + 1
            )

    def parse(self):
        program = self.parse_program()
        self.consume("EOF")
        return program

    def parse_program(self):
        statements = []
        while self.current_token.type != "EOF":
            statements.append(self.parse_statement())
        return Program(statements)

    def parse_statement(self):
        token_type = self.current_token.type
        if token_type in ("VAR", "CONST"):
            return self.parse_vardecl()
        elif token_type == "IMPORT" and self.peek().type == "FUNC":
            return self.parse_funcdecl()
        elif token_type == "FUNC":
            return self.parse_funcdecl()
        elif token_type == "IF":
            return self.parse_if_stmt()
        elif token_type == "WHILE":
            return self.parse_while_stmt()
        elif token_type == "BREAK":
            return self.parse_break_stmt()
        elif token_type == "CONTINUE":
            return self.parse_continue_stmt()
        elif token_type == "RETURN":
            return self.parse_return_stmt()
        elif token_type == "PRINT":
            return self.parse_print_stmt()
        elif token_type in ("ID", "DEREF"):
            return self.parse_assignment()
        else:
            raise SyntaxError(
                f"Unexpected token {self.current_token.type} at line {self.current_token.line}, column {self.current_token.column}"
            )

    def parse_assignment(self):
        location = self.parse_location()
        self.consume("ASSIGN")
        expr = self.parse_expression()
        self.consume("SEMI")
        return Assignment(location, expr)

    def parse_vardecl(self):
        kind = self.current_token.value
        self.consume(kind.upper())
        id_token = self.consume("ID")
        identifier = id_token.value
        var_type = None
        if self.current_token.type in ("INT", "FLOAT", "CHAR", "BOOL"):
            var_type = Type(self.consume().value)
        initializer = None
        if self.current_token.type == "ASSIGN":
            self.consume("ASSIGN")
            initializer = self.parse_expression()
        self.consume("SEMI")
        return VarDecl(kind, identifier, var_type, initializer)

    def parse_funcdecl(self):
        is_import = False
        if self.current_token.type == "IMPORT":
            self.consume("IMPORT")
            is_import = True
        self.consume("FUNC")
        id_token = self.consume("ID")
        func_name = id_token.value
        self.consume("LPAREN")
        params = self.parse_parameters()
        self.consume("RPAREN")
        return_type = Type(self.consume().value)
        self.consume("LBRACE")
        body = []
        while self.current_token.type != "RBRACE":
            body.append(self.parse_statement())
        self.consume("RBRACE")
        return FuncDecl(is_import, func_name, params, return_type, body)

    def parse_parameters(self):
        params = []
        if self.current_token.type == "ID":
            param_id = self.consume("ID").value
            param_type = Type(self.consume().value)
            params.append((param_id, param_type))
            while self.current_token.type == "COMMA":
                self.consume("COMMA")
                param_id = self.consume("ID").value
                param_type = Type(self.consume().value)
                params.append((param_id, param_type))
        return Parameters(params)

    def parse_if_stmt(self):
        self.consume("IF")
        condition = self.parse_expression()
        self.consume("LBRACE")
        then_block = []
        while self.current_token.type != "RBRACE":
            then_block.append(self.parse_statement())
        self.consume("RBRACE")
        else_block = []
        if self.current_token.type == "ELSE":
            self.consume("ELSE")
            self.consume("LBRACE")
            while self.current_token.type != "RBRACE":
                else_block.append(self.parse_statement())
            self.consume("RBRACE")
        return IfStmt(condition, then_block, else_block)

    def parse_while_stmt(self):
        self.consume("WHILE")
        condition = self.parse_expression()
        self.consume("LBRACE")
        body = []
        while self.current_token.type != "RBRACE":
            body.append(self.parse_statement())
        self.consume("RBRACE")
        return WhileStmt(condition, body)

    def parse_break_stmt(self):
        self.consume("BREAK")
        self.consume("SEMI")
        return BreakStmt()

    def parse_continue_stmt(self):
        self.consume("CONTINUE")
        self.consume("SEMI")
        return ContinueStmt()

    def parse_return_stmt(self):
        self.consume("RETURN")
        expr = self.parse_expression()
        self.consume("SEMI")
        return ReturnStmt(expr)

    def parse_print_stmt(self):
        self.consume("PRINT")
        expr = self.parse_expression()
        self.consume("SEMI")
        return PrintStmt(expr)

    def parse_location(self):
        if self.current_token.type == "ID":
            id_token = self.consume("ID")
            return IdentifierLocation(id_token.value)
        elif self.current_token.type == "DEREF":
            self.consume("DEREF")
            expr = self.parse_expression()
            return DereferenceLocation(expr)
        else:
            raise SyntaxError(
                f"Expected location, got {self.current_token.type} at line {self.current_token.line}, column {self.current_token.column}"
            )

    def parse_expression(self):
        return self.parse_or_term()

    def parse_or_term(self):
        node = self.parse_and_term()
        while self.current_token.type == "LOR":
            op = self.consume().value
            right = self.parse_and_term()
            node = BinaryOp(node, op, right)
        return node

    def parse_and_term(self):
        node = self.parse_rel_term()
        while self.current_token.type == "LAND":
            op = self.consume().value
            right = self.parse_rel_term()
            node = BinaryOp(node, op, right)
        return node

    def parse_rel_term(self):
        node = self.parse_add_term()
        while self.current_token.type in ("LT", "GT", "LE", "GE", "EQ", "NE"):
            op = self.consume().value
            right = self.parse_add_term()
            node = BinaryOp(node, op, right)
        return node

    def parse_add_term(self):
        node = self.parse_mul_term()
        while self.current_token.type in ("PLUS", "MINUS"):
            op = self.consume().value
            right = self.parse_mul_term()
            node = BinaryOp(node, op, right)
        return node

    def parse_mul_term(self):
        node = self.parse_factor()
        while self.current_token.type in ("TIMES", "DIVIDE"):
            op = self.consume().value
            right = self.parse_factor()
            node = BinaryOp(node, op, right)
        return node

    def parse_factor(self):
        token = self.current_token
        if token.type in ("INTEGER", "FLOAT", "CHAR", "TRUE", "FALSE"):
            self.consume()
            return Literal(token.value, token.type)
        elif token.type in ("PLUS", "MINUS", "GROW"):
            op = self.consume().value
            expr = self.parse_expression()
            return UnaryOp(op, expr)
        elif token.type == "LPAREN":
            self.consume("LPAREN")
            expr = self.parse_expression()
            self.consume("RPAREN")
            return expr
        elif token.type in ("INT", "FLOAT", "CHAR", "BOOL"):
            cast_type = self.consume().value
            self.consume("LPAREN")
            expr = self.parse_expression()
            self.consume("RPAREN")
            return Cast(cast_type, expr)
        elif token.type == "ID":
            if self.peek().type == "LPAREN":
                func_name = token.value
                self.consume("ID")
                self.consume("LPAREN")
                args = self.parse_arguments()
                self.consume("RPAREN")
                return FunctionCall(func_name, args)
            else:
                return self.parse_location()
        elif token.type == "DEREF":
            return self.parse_location()
        else:
            raise SyntaxError(
                f"Unexpected token {token.type} in factor at line {token.line}, column {token.column}"
            )

    def parse_arguments(self):
        args = []
        if self.current_token.type != "RPAREN":
            args.append(self.parse_expression())
            while self.current_token.type == "COMMA":
                self.consume("COMMA")
                args.append(self.parse_expression())
        return args
