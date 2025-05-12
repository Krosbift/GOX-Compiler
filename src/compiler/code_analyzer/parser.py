from ..shared.AST.grammar.program import Program
from ..shared.AST.grammar.assigment import Assignment
from ..shared.AST.grammar.vardecl import VarDecl
from ..shared.AST.grammar.funcdecl import FuncDecl
from ..shared.AST.grammar.if_stmt import IfStmt
from ..shared.AST.grammar.while_stmt import WhileStmt
from ..shared.AST.grammar.break_stmt import BreakStmt
from ..shared.AST.grammar.continue_stmt import ContinueStmt
from ..shared.AST.grammar.return_stmt import ReturnStmt
from ..shared.AST.grammar.print_stmt import PrintStmt
from ..shared.AST.grammar.parameters import Parameters
from ..shared.AST.grammar.binary_operator import BinaryOp
from ..shared.AST.grammar.unary_operator import UnaryOp
from ..shared.AST.grammar.literal import Literal
from ..shared.AST.grammar.identifier_location import IdentifierLocation
from ..shared.AST.grammar.dereference_location import DereferenceLocation
from ..shared.AST.grammar.function_call import FunctionCall
from ..shared.AST.grammar.cast import Cast
from .helpers.parser import ParserHelper
from .errors.parser import ParserError
from ..shared.grammar.gox_token import Token


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

    def analyze(self):
        self.errors = []
        return self.program()

    def program(self):
        """
        ### statement* EOF
        """
        statements = []
        while self.current_token and self.current_token.type != "EOF":
            statements.append(self.statement())

        if len(self.errors) > 0:
            return ParserError(self.errors).print_errors()

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
        if self.current_token and self.current_token.type == "ID":
            if ParserHelper.peek_token(self).type == "ASSIGN":
                return self.assignment()
            elif ParserHelper.peek_token(self).type == "LPAREN":
                return self.func_call()
            else:
                token_type, value, line_number, column_number = (
                    self.current_token
                    if self.current_token
                    else (None, None, None, None)
                )
                self.errors.append(
                    (
                        Token(token_type, value, line_number, column_number),
                        (
                            f"Se esperaba el token ASSIGN / LPAREN en la linea "
                            f"{line_number}, columna {column_number}. Pero se encontró "
                            f"el token {token_type}"
                        ),
                    )
                )
                self.next_token()
        elif self.current_token and self.current_token.type == ("DEREF"):
            return self.assignment()
        elif self.current_token and self.current_token.type in ("VAR", "CONST"):
            return self.vardecl()
        elif self.current_token and self.current_token.type in ("FUNC", "IMPORT"):
            return self.funcdecl()
        elif self.current_token and self.current_token.type == "IF":
            return self.if_stmt()
        elif self.current_token and self.current_token.type == "WHILE":
            return self.while_stmt()
        elif self.current_token and self.current_token.type == "BREAK":
            return self.break_stmt()
        elif self.current_token and self.current_token.type == "CONTINUE":
            return self.continue_stmt()
        elif self.current_token and self.current_token.type == "RETURN":
            return self.return_stmt()
        elif self.current_token and self.current_token.type == "PRINT":
            return self.print_stmt()
        else:
            token_type, value, line_number, column_number = (
                self.current_token if self.current_token else (None, None, None, None)
            )
            self.errors.append(
                (
                    Token(token_type, value, line_number, column_number),
                    (
                        f"Se esperaba el token VAR / CONST / FUNC / IF / WHILE / BREAK / "
                        f"CONTINUE / RETURN / PRINT en la linea {line_number}, columna "
                        f"{column_number}. Pero se encontró el token {token_type}"
                    ),
                )
            )
            self.next_token()

    def assignment(self):
        """
        ### location '=' expression ';'
        """
        location = self.location()
        ParserHelper.expect(self, "ASSIGN")
        expression = self.expression()
        ParserHelper.expect(self, "SEMI")
        return Assignment(location, expression)

    def vardecl(self):
        """
        ### ('var' / 'const') ID type? ('=' expression)? ';'
        """
        kind = self.current_token.type if self.current_token else None
        self.next_token()
        identifier = self.current_token.value if self.current_token else None
        ParserHelper.expect(self, "ID")
        var_type = None
        if self.current_token.type in ("INT", "FLOAT_TYPE", "CHAR_TYPE", "BOOL"):
            var_type = self.current_token.value
            self.next_token()
        initializer = None
        if self.current_token.type == "ASSIGN":
            self.next_token()
            initializer = self.expression()
        ParserHelper.expect(self, "SEMI")
        return VarDecl(kind, identifier, var_type, initializer)

    def funcdecl(self):
        """
        ### 'import'? 'func' ID '(' parameters ')' type '{' statement* '}'
        """
        is_import = False
        if self.current_token.type == "IMPORT":
            is_import = True
            self.next_token()
        ParserHelper.expect(self, "FUNC")
        identifier = self.current_token.value
        ParserHelper.expect(self, "ID")
        ParserHelper.expect(self, "LPAREN")
        parameters = self.parameters()
        ParserHelper.expect(self, "RPAREN")
        return_type = ParserHelper.expect_type(self)
        body = []
        if not is_import:
            ParserHelper.expect(self, "LBRACE")
            while self.current_token and self.current_token.type != "RBRACE":
                body.append(self.statement())
            ParserHelper.expect(self, "RBRACE")
        else:
            ParserHelper.expect(self, "SEMI")
        return FuncDecl(is_import, identifier, parameters, return_type, body)

    def if_stmt(self):
        """
        ### 'if' expression '{' statement* '}' ('else' '{' statement* '}')?
        """
        ParserHelper.expect(self, "IF")
        condition = self.expression()
        ParserHelper.expect(self, "LBRACE")
        then_block = []
        while self.current_token.type != "RBRACE":
            then_block.append(self.statement())
        ParserHelper.expect(self, "RBRACE")
        else_block = None
        if self.current_token:
            if self.current_token.type == "ELSE":
                self.next_token()
                ParserHelper.expect(self, "LBRACE")
                else_block = []
                while self.current_token.type != "RBRACE":
                    else_block.append(self.statement())
                ParserHelper.expect(self, "RBRACE")
        return IfStmt(condition, then_block, else_block)

    def while_stmt(self):
        """
        ### 'while' expression '{' statement* '}'
        """
        ParserHelper.expect(self, "WHILE")
        condition = self.expression()
        ParserHelper.expect(self, "LBRACE")
        body = []
        while self.current_token.type != "RBRACE":
            body.append(self.statement())
        ParserHelper.expect(self, "RBRACE")
        return WhileStmt(condition, body)

    def break_stmt(self):
        """
        ### 'break' ';'
        """
        ParserHelper.expect(self, "BREAK")
        ParserHelper.expect(self, "SEMI")
        return BreakStmt()

    def continue_stmt(self):
        """
        ### 'continue' ';'
        """
        ParserHelper.expect(self, "CONTINUE")
        ParserHelper.expect(self, "SEMI")
        return ContinueStmt()

    def return_stmt(self):
        """
        ### 'return' expression ';'
        """
        ParserHelper.expect(self, "RETURN")
        expression = self.expression()
        ParserHelper.expect(self, "SEMI")
        return ReturnStmt(expression)

    def print_stmt(self):
        """
        ### 'print' expression ';'
        """
        ParserHelper.expect(self, "PRINT")
        expression = self.expression()
        ParserHelper.expect(self, "SEMI")
        return PrintStmt(expression)

    def parameters(self):
        """
        ### ID type (',' ID type)* / empty
        """
        params = []
        if self.current_token.type != "RPAREN":
            param_name = self.current_token.value
            ParserHelper.expect(self, "ID")
            param_type = ParserHelper.expect_type(self)
            params.append((param_name, param_type))
            while self.current_token.type == "COMMA":
                self.next_token()
                param_name = self.current_token.value
                ParserHelper.expect(self, "ID")
                param_type = ParserHelper.expect_type(self)
                params.append((param_name, param_type))
        return Parameters(params)

    def expression(self):
        return self.orterm()

    def orterm(self):
        return self._parse_binary_op(self.andterm, ("LOR",))

    def andterm(self):
        return self._parse_binary_op(self.relterm, ("LAND",))

    def relterm(self):
        return self._parse_binary_op(self.addterm, ("LT", "GT", "LE", "GE", "EQ", "NE"))

    def addterm(self):
        return self._parse_binary_op(self.multterm, ("PLUS", "MINUS"))

    def multterm(self):
        return self._parse_binary_op(self.unaryterm, ("TIMES", "DIVIDE"))

    def _parse_binary_op(self, higher_precedence_method, op_types):
        """Función helper genérica para parsear operadores binarios izquierdas-asociativos."""
        node = higher_precedence_method()
        while self.current_token and self.current_token.type in op_types:
            op_token = self.current_token
            self.next_token()
            right_node = higher_precedence_method()
            node = BinaryOp(node, op_token.value, right_node)
        return node

    def unaryterm(self):
        """
        Handles unary operators like +, -, !, ^, and ` (dereference as R-value).
        unary_op_term <- ('+' / '-' / '^' / '!' / '`') unary_op_term
                      / primary_expression
        """
        token = self.current_token
        if token:
            if token.type in ("PLUS", "MINUS", "GROW", "NOT"):
                op_token = token
                self.next_token()
                operand = self.unaryterm()
                return UnaryOp(op_token.value, operand)
            elif token.type == "DEREF":
                op_token = token
                self.next_token()
                address_expression = self.unaryterm()
                deref_node = DereferenceLocation(address_expression)
                if hasattr(deref_node, "token"):
                    deref_node.token = op_token
                return deref_node

        return self.primary()

    def primary(
        self,
    ):
        """
        expression <- literal
            / ID
            / ID '(' arguments ')'
            / '(' expression ')'
            / type '(' expression ')'
        """
        token = self.current_token
        if not token:
            return None

        if token.type in ("INTEGER", "FLOAT", "CHAR", "TRUE", "FALSE"):
            literal_token = token
            self.next_token()
            return Literal(literal_token.value, literal_token.type)

        elif token.type == "LPAREN":
            self.next_token()
            expr = self.expression()
            ParserHelper.expect(self, "RPAREN")
            return expr

        elif token.type in (
            "INT",
            "FLOAT_TYPE",
            "CHAR_TYPE",
            "BOOL",
        ):
            cast_type_token = token
            self.next_token()
            ParserHelper.expect(self, "LPAREN")
            expr = self.expression()
            ParserHelper.expect(self, "RPAREN")
            return Cast(cast_type_token.value, expr)

        elif token.type == "ID":
            id_token = token
            name = token.value
            self.next_token()
            if self.current_token and self.current_token.type == "LPAREN":
                self.next_token()
                args = self.arguments()
                ParserHelper.expect(self, "RPAREN")
                return FunctionCall(name, args)
            else:
                return IdentifierLocation(name)
        else:
            token_type, value, line, col = (
                token.type,
                token.value,
                token.line,
                token.column,
            )
            self.errors.append(
                (
                    token,
                    (
                        f"Token inesperado '{value}' ({token_type}) en la línea {line}, columna {col} al esperar un primario (literal, ID, '(', tipo)."
                    ),
                )
            )
            self.next_token()

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
        location <- ID
                / '`' expression
        """
        token = self.current_token
        if token and token.type == "ID":
            id_token = token
            self.next_token()
            return IdentifierLocation(id_token.value)
        elif token and token.type == "DEREF":
            deref_op_token = token
            self.next_token()
            address_expr = self.unaryterm()
            deref_node = DereferenceLocation(address_expr)
            if hasattr(deref_node, "token"):
                deref_node.token = deref_op_token
            return deref_node
        else:
            token_type, value, line_number, column_number = (
                self.current_token if self.current_token else (None, None, None, None)
            )
            self.errors.append(
                (
                    Token(token_type, value, line_number, column_number),
                    (
                        f"Se esperaba el token ID / DEREF en la linea {line_number}, "
                        f"columna {column_number}. Pero se encontró el token {token_type}"
                    ),
                )
            )
            self.next_token()

    def func_call(self):
        """
        ### ID '(' arguments ')'
        """
        name = self.current_token.value
        self.next_token()
        ParserHelper.expect(self, "LPAREN")
        args = self.arguments()
        ParserHelper.expect(self, "RPAREN")
        ParserHelper.expect(self, "SEMI")
        return FunctionCall(name, args)
