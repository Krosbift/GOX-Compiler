from typing import Type
from .errors.checker import CheckerError
from .helpers.check import SymbolTablePrinter
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
from ..shared.grammar.gox_token import Token
from ..shared.symtable.symbol import Symbol, SymbolKind
from ..shared.symtable.symtable import SymbolTable

class Checker:
    def __init__(self, ast):
        self.ast = ast
        self.symbol_table = SymbolTable()
        self.errors = []
        self.expected_deref_type: str | None = None

    def _get_node_location(self, node_or_token) -> tuple[str, str]:
        line, col = "N/A", "N/A"
        token_to_check = None
        if isinstance(node_or_token, Token):
            token_to_check = node_or_token
        elif hasattr(node_or_token, "token") and isinstance(node_or_token.token, Token):
            token_to_check = node_or_token.token
        elif hasattr(node_or_token, "op_token") and isinstance(
            node_or_token.op_token, Token
        ):
            token_to_check = node_or_token.op_token
        elif hasattr(node_or_token, "id_token") and isinstance(
            node_or_token.id_token, Token
        ):
            token_to_check = node_or_token.id_token
        if (
            not token_to_check
            and hasattr(node_or_token, "line")
            and hasattr(node_or_token, "column")
        ):
            if node_or_token.line is not None and node_or_token.column is not None:
                line, col = node_or_token.line, node_or_token.column
        if token_to_check:
            line, col = token_to_check.line, token_to_check.column
        return str(line), str(col)

    def _add_error(self, message: str, node_or_token_for_loc):
        line, col = self._get_node_location(node_or_token_for_loc)
        full_message = f"Error Semántico (Línea {line}, Col {col}): {message}"
        self.errors.append(full_message)

    def analyze(self):
        self.errors = []
        self.symbol_table = SymbolTable()
        self._visit(self.ast)
        if self.errors:
            return CheckerError(self.errors).print_errors()
        SymbolTablePrinter(self.symbol_table).print_table()
        return self.symbol_table

    def _visit(
        self, node, expected_type_hint: str | None = None
    ):
        if node is None:
            return None
        previous_expected_deref_type = self.expected_deref_type
        if expected_type_hint:
            self.expected_deref_type = expected_type_hint
        method_name = f"_visit_{node.__class__.__name__}"
        visitor = getattr(self, method_name, self._generic_visit)
        result_type = visitor(node)
        if expected_type_hint:
            self.expected_deref_type = previous_expected_deref_type
        if (
            hasattr(node, "__module__")
            and "AST.grammar" in node.__module__
            and result_type is not None
        ):
            if not isinstance(
                node,
                (
                    Program,
                    VarDecl,
                    FuncDecl,
                    IfStmt,
                    WhileStmt,
                    BreakStmt,
                    ContinueStmt,
                    ReturnStmt,
                    PrintStmt,
                    Assignment,
                    Parameters,
                ),
            ):
                node.semantic_type = result_type
        return result_type

    def _generic_visit(self, node):
        for field_name, field_value in vars(node).items():
            if isinstance(field_value, list):
                for item in field_value:
                    if hasattr(item, "__module__") and "AST.grammar" in item.__module__:
                        self._visit(item)
            elif (
                hasattr(field_value, "__module__")
                and "AST.grammar" in field_value.__module__
            ):
                self._visit(field_value)
        return None

    def _visit_Program(self, node: Program):
        node.semantic_scope = self.symbol_table.global_scope
        program_body_scope = self.symbol_table.global_scope
        node.program_body_semantic_scope = program_body_scope
        for stmt in node.statements:
            self._visit(stmt)

    def _visit_VarDecl(self, node: VarDecl):
        var_name = node.identifier
        declared_type_str = node.var_type
        if declared_type_str and declared_type_str not in self.symbol_table.valid_types:
            declared_type_str = None
        initializer_type = None
        if node.initializer:
            initializer_type = self._visit(
                node.initializer, expected_type_hint=declared_type_str
            )
        actual_type = None
        if declared_type_str:
            actual_type = declared_type_str
            if initializer_type and not self.symbol_table.is_type_assignable(
                declared_type_str, initializer_type
            ):
                self._add_error(
                    f"No se puede inicializar variable '{var_name}' (tipo '{declared_type_str}') con un valor de tipo '{initializer_type}'.",
                    node.initializer or node,
                )
        elif initializer_type:
            actual_type = initializer_type
        else:
            node.semantic_type = None
            node.defined_symbol = None
            return
        if not actual_type:
            node.semantic_type = None
            node.defined_symbol = None
            return
        node.semantic_type = actual_type
        symbol_kind = (
            SymbolKind.CONSTANT
            if (node.kind == "const" or node.kind == "CONST")
            else SymbolKind.VARIABLE
        )
        symbol = Symbol(
            var_name,
            symbol_kind,
            actual_type,
            node=node.identifier_token if hasattr(node, "identifier_token") else node,
        )
        symbol.initialized = (node.initializer is not None) or (
            symbol_kind == SymbolKind.CONSTANT
        )
        node.defined_symbol = symbol
        if not self.symbol_table.current_scope.define(symbol):
            pass

    def _visit_Assignment(self, node: Assignment):
        expected_type_for_rhs = None
        if isinstance(node.location, IdentifierLocation):
            var_symbol = self.symbol_table.current_scope.lookup(node.location.name)
            if var_symbol:
                expected_type_for_rhs = var_symbol.type
        elif isinstance(node.location, DereferenceLocation):
            pass
        expr_type = self._visit(
            node.expression, expected_type_hint=expected_type_for_rhs
        )
        if expr_type is None:
            if isinstance(node.location, IdentifierLocation):
                node.location.semantic_type = None
            elif isinstance(node.location, DereferenceLocation):
                node.location.semantic_type = None
            return
        if isinstance(node.location, IdentifierLocation):
            var_name = node.location.name
            symbol = self.symbol_table.current_scope.lookup(var_name)
            if not symbol:
                self._add_error(
                    f"Asignación a variable no declarada '{var_name}'.", node.location
                )
                return
            if symbol.kind == SymbolKind.CONSTANT:
                self._add_error(
                    f"No se puede asignar a la constante '{var_name}'.", node.location
                )
                return
            if symbol.kind == SymbolKind.FUNCTION:
                self._add_error(
                    f"No se puede asignar a un nombre de función '{var_name}'.",
                    node.location,
                )
                return
            if not self.symbol_table.is_type_assignable(symbol.type, expr_type):
                self._add_error(
                    f"No se puede asignar un valor de tipo '{expr_type}' a la variable '{var_name}' de tipo '{symbol.type}'.",
                    node.expression,
                )
            symbol.initialized = True
            node.location.semantic_type = symbol.type
            node.location.referenced_symbol = symbol
        elif isinstance(node.location, DereferenceLocation):
            node.location.semantic_type = expr_type
            self._visit(
                node.location.expression, expected_type_hint="int"
            )

    def _visit_BinaryOp(self, node: BinaryOp):
        left_type = self._visit(node.left)
        right_type = self._visit(node.right)
        if (
            isinstance(node.left, DereferenceLocation)
            and node.left.semantic_type is None
            and right_type
        ):
            node.left.semantic_type = right_type
            left_type = right_type
        if (
            isinstance(node.right, DereferenceLocation)
            and node.right.semantic_type is None
            and left_type
        ):
            node.right.semantic_type = left_type
            right_type = left_type
        if left_type is None or right_type is None:
            node.semantic_type = None
            return None
        op_char = node.op
        result_type = self.symbol_table.get_binary_op_result_type(
            op_char, left_type, right_type
        )
        if result_type is None:
            self._add_error(
                f"Operador binario '{op_char}' no se puede aplicar a operandos de tipo '{left_type}' y '{right_type}'.",
                node.op_token or node,
            )
            node.semantic_type = None
            return None
        node.semantic_type = result_type
        return result_type

    def _visit_UnaryOp(self, node: UnaryOp):
        expected_hint_for_operand = "int" if node.op == "^" else None
        expr_type = self._visit(
            node.expr, expected_type_hint=expected_hint_for_operand
        )
        if expr_type is None:
            node.semantic_type = None
            return None
        if node.op == "^" and expr_type != "int":
            self._add_error(
                f"Operador unario '{node.op}' (GROW) espera un operando de tipo 'int', pero se encontró '{expr_type}'.",
                node.expr,
            )
            node.semantic_type = None
            return None
        result_type = self.symbol_table.get_unary_op_result_type(node.op, expr_type)
        if result_type is None:
            if node.op != "^":
                self._add_error(
                    f"Operador unario '{node.op}' no se puede aplicar a un operando de tipo '{expr_type}'.",
                    node.op_token or node,
                )
            node.semantic_type = None
            return None
        node.semantic_type = result_type
        return result_type

    def _visit_Literal(self, node: Literal):
        ttype = node.type_token
        result_type_str = None
        if ttype == "INTEGER":
            result_type_str = "int"
        elif ttype == "FLOAT":
            result_type_str = "float"
        elif ttype == "CHAR":
            result_type_str = "char"
        elif ttype == "TRUE" or ttype == "FALSE":
            result_type_str = "bool"
        else:
            self._add_error(f"Tipo de literal desconocido o inesperado: {ttype}", node)
        node.semantic_type = result_type_str
        return result_type_str

    def _visit_IdentifierLocation(self, node: IdentifierLocation):
        name = node.name
        symbol = self.symbol_table.current_scope.lookup(name)
        node.referenced_symbol = symbol
        if not symbol:
            self._add_error(f"Uso de identificador no declarado '{name}'.", node)
            node.semantic_type = None
            return None
        if symbol.kind == SymbolKind.FUNCTION:
            self._add_error(
                f"El nombre de función '{name}' no puede ser usado como un valor directamente.",
                node,
            )
            node.semantic_type = None
            return None
        node.semantic_type = symbol.type
        return symbol.type

    def _visit_DereferenceLocation(self, node: DereferenceLocation):
        self._visit(node.expression, expected_type_hint="int")
        if (
            not hasattr(node.expression, "semantic_type")
            or node.expression.semantic_type != "int"
        ):
            if (
                hasattr(node.expression, "semantic_type")
                and node.expression.semantic_type is not None
            ):
                self._add_error(
                    f"La expresión para desreferenciar debe evaluarse a 'int' (dirección), pero es '{node.expression.semantic_type}'.",
                    node.expression,
                )
            node.semantic_type = None
            return None
        type_of_value = None
        if self.expected_deref_type:
            type_of_value = self.expected_deref_type
        else:
            type_of_value = "int"
        node.semantic_type = type_of_value
        return type_of_value

    def _visit_FuncDecl(self, node: FuncDecl):
        func_name = node.identifier
        declared_type_str = node.return_type
        if (
            declared_type_str and declared_type_str not in self.symbol_table.valid_types
        ):
            declared_type_str = None
        params_info = []
        if node.parameters and node.parameters.params:
            for p_idx, (p_name_str, p_type_str) in enumerate(
                node.parameters.params
            ):
                params_info.append(
                    {
                        "name": p_name_str,
                        "type": (
                            p_type_str
                            if p_type_str in self.symbol_table.valid_types
                            else None
                        ),
                        "node": node.parameters,
                    }
                )
        func_symbol = Symbol(
            func_name,
            SymbolKind.FUNCTION,
            sym_type=declared_type_str,
            node=node.id_token if hasattr(node, "id_token") else node,
            params_info=params_info,
            return_type=declared_type_str,
            is_import=node.is_import,
        )
        node.defined_symbol = func_symbol
        if not self.symbol_table.current_scope.lookup(
            func_name, current_scope_only=True
        ):
            self.symbol_table.current_scope.define(func_symbol)
        if node.is_import:
            return
        func_body_scope = self.symbol_table.enter_scope(
            scope_name=f"<func_body_{func_name}>", current_function_symbol=func_symbol
        )
        node.body_semantic_scope = func_body_scope
        for p_info in params_info:
            if p_info["type"]:
                param_sym = Symbol(
                    p_info["name"],
                    SymbolKind.PARAMETER,
                    p_info["type"],
                    node=p_info["node"],
                )
                self.symbol_table.current_scope.define(param_sym)
        for stmt in node.body:
            self._visit(stmt)
        self.symbol_table.exit_scope()

    def _visit_FunctionCall(self, node: FunctionCall):
        func_name = node.name
        func_symbol = self.symbol_table.current_scope.lookup(func_name)
        node.referenced_symbol = func_symbol
        if not func_symbol:
            node.semantic_type = None
            return None
        if func_symbol.kind != SymbolKind.FUNCTION:
            node.semantic_type = None
            return None
        if node.arguments:
            for i, arg_expr_node in enumerate(node.arguments):
                expected_param_type_for_arg = (
                    func_symbol.params_info[i]["type"]
                    if i < len(func_symbol.params_info)
                    else None
                )
                passed_arg_type = self._visit(
                    arg_expr_node, expected_type_hint=expected_param_type_for_arg
                )
        node.semantic_type = (
            func_symbol.return_type
        )
        return func_symbol.return_type

    def _visit_IfStmt(self, node: IfStmt):
        self._visit(
            node.condition, expected_type_hint="bool"
        )
        if (
            node.condition.semantic_type is not None
            and node.condition.semantic_type != "bool"
        ):
            self._add_error(
                f"La condición de 'if' debe ser 'bool', pero es '{node.condition.semantic_type}'.",
                node.condition,
            )
        then_scope = self.symbol_table.enter_scope(scope_name="<if_then_block>")
        node.then_block_semantic_scope = then_scope
        for stmt in node.then_block:
            self._visit(stmt)
        self.symbol_table.exit_scope()
        if node.else_block:
            else_scope = self.symbol_table.enter_scope(scope_name="<if_else_block>")
            node.else_block_semantic_scope = else_scope
            for stmt in node.else_block:
                self._visit(stmt)
            self.symbol_table.exit_scope()
        else:
            node.else_block_semantic_scope = None

    def _visit_WhileStmt(self, node: WhileStmt):
        self._visit(
            node.condition, expected_type_hint="bool"
        )
        if (
            node.condition.semantic_type is not None
            and node.condition.semantic_type != "bool"
        ):
            self._add_error(
                f"La condición de 'while' debe ser 'bool', pero es '{node.condition.semantic_type}'.",
                node.condition,
            )
        body_scope = self.symbol_table.enter_scope(
            scope_name="<while_body>", is_loop=True
        )
        node.body_semantic_scope = body_scope
        for stmt in node.body:
            self._visit(stmt)
        self.symbol_table.exit_scope()

    def _visit_ReturnStmt(self, node: ReturnStmt):
        current_func_sym = self.symbol_table.current_scope.get_current_function_symbol()
        if not current_func_sym:
            self._visit(
                node.expression
            )
            return
        current_func_sym.has_return_statement = True
        expected_return_type = current_func_sym.return_type
        returned_expr_type = self._visit(
            node.expression, expected_type_hint=expected_return_type
        )
        if returned_expr_type is None:
            return
        if expected_return_type is None:
            return
        if not self.symbol_table.is_type_assignable(
            expected_return_type, returned_expr_type
        ):
            self._add_error(f"...", node.expression)

    def _visit_PrintStmt(self, node: PrintStmt):
        expr_type = self._visit(
            node.expression
        )
        if expr_type is None:
            return
        allowed_print_types = {"int", "float", "char", "bool"}
        if expr_type not in allowed_print_types:
            self._add_error(
                f"No se puede usar 'print' con tipo '{expr_type}'.", node.expression
            )

    def _visit_Cast(self, node: Cast):
        target_type_str = node.cast_type
        if (
            target_type_str not in self.symbol_table.valid_types
            or target_type_str == "void"
        ):
            self._visit(node.expression)
            node.semantic_type = None
            return None
        source_expr_type = self._visit(
            node.expression
        )
        if source_expr_type is None:
            node.semantic_type = None
            return None
        if not self.symbol_table.is_type_castable(target_type_str, source_expr_type):
            self._add_error(
                f"No se puede castear de '{source_expr_type}' a '{target_type_str}'.",
                node,
            )
            node.semantic_type = None
            return None
        node.semantic_type = target_type_str
        return target_type_str

    def _visit_Parameters(self, node: Parameters):
        pass

    def _visit_Type(self, node: Type):
        if node.name not in self.symbol_table.valid_types:
            self._add_error(
                f"Nombre de tipo '{node.name}' desconocido o inválido.", node
            )
            return None
        return node.name
