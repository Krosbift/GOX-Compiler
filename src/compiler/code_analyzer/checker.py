from typing import Type
from .errors.checker import CheckerError
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
from ..shared.grammar.gox_token import Token

class Checker:
    def __init__(self, ast):
        self.ast = ast
        self.symbol_table = SymbolTable()
        self.errors = []

    def _get_node_location(self, node_or_token) -> tuple[str, str]:
        """Intenta obtener la línea y columna de un nodo o token."""
        line, col = "N/A", "N/A"

        token_to_check = None
        if isinstance(node_or_token, Token):
            token_to_check = node_or_token
        elif hasattr(node_or_token, "token"):
            if isinstance(node_or_token.token, Token):
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
        self.symbol_table = (
            SymbolTable()
        )

        # Podrías pre-registrar funciones built-in aquí si tu lenguaje las tiene
        # ej: self.symbol_table.global_scope.define(Symbol("readInt", SymbolKind.FUNCTION, ...))

        self._visit(self.ast)

        if self.errors:
            print(self.errors)
            return CheckerError(self.errors).print_errors()
        return self.symbol_table

    def _visit(self, node):
        if node is None:
            return None
        method_name = f"_visit_{node.__class__.__name__}"
        visitor = getattr(self, method_name, self._generic_visit)
        return visitor(node)

    def _generic_visit(self, node):
        return None

    def _visit_Program(self, node: Program):
        self.symbol_table.enter_scope("<program_body>")
        for stmt in node.statements:
            self._visit(stmt)
        self.symbol_table.exit_scope()

    def _visit_VarDecl(self, node: VarDecl):
        # `VarDecl(kind, identifier_token, var_type_str, initializer_expr)`
        var_name = (
            node.identifier
        )  # Si `identifier` es un string, necesitas el token para la ubicación.
        # Mejor si `node.id_token` es el Token.
        id_token_for_loc = (
            node.identifier_token if hasattr(node, "identifier_token") else node
        )

        if self.symbol_table.current_scope.lookup(var_name, current_scope_only=True):
            self._add_error(
                f"Identificador '{var_name}' ya declarado en este ámbito.",
                id_token_for_loc,
            )
            return

        declared_type_str = node.var_type  # String del tipo ej: 'int', o None
        if declared_type_str and declared_type_str not in self.symbol_table.valid_types:
            type_token_for_loc = (
                node.type_token if hasattr(node, "type_token") else node
            )
            self._add_error(
                f"Tipo desconocido '{declared_type_str}' para variable '{var_name}'.",
                type_token_for_loc,
            )
            declared_type_str = (
                None  # Tratar como no tipado para evitar errores cascada
            )

        initializer_type = None
        if node.initializer:
            initializer_type = self._visit(node.initializer)
            # Si initializer_type es None, un error ya fue reportado en la expresión

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
        elif initializer_type:  # Inferencia de tipo
            actual_type = initializer_type
        else:
            if node.kind == "const" or node.kind == "CONST":  # 'CONST' es tu token
                self._add_error(
                    f"Constante '{var_name}' debe ser inicializada.", id_token_for_loc
                )
            else:  # 'var'
                self._add_error(
                    f"Variable '{var_name}' debe tener un tipo explícito o ser inicializada para inferir su tipo.",
                    id_token_for_loc,
                )
            return

        if not actual_type:  # Si no se pudo determinar el tipo
            return

        symbol_kind = (
            SymbolKind.CONSTANT
            if (node.kind == "const" or node.kind == "CONST")
            else SymbolKind.VARIABLE
        )
        # El `node` para el símbolo debería ser el token de identificación para mejor ubicación de errores de "ya declarado"
        symbol = Symbol(var_name, symbol_kind, actual_type, node=id_token_for_loc)
        symbol.initialized = (node.initializer is not None) or (
            symbol_kind == SymbolKind.CONSTANT
        )

        if not self.symbol_table.current_scope.define(symbol):
            # Esto no debería pasar si el lookup inicial funcionó, pero por si acaso.
            self._add_error(
                f"Fallo al definir el símbolo '{var_name}' (posiblemente un error interno).",
                id_token_for_loc,
            )

    def _visit_Assignment(self, node: Assignment):
        # `Assignment(location_node, expression_node)`
        # `location_node` puede ser `IdentifierLocation` o `DereferenceLocation`

        # Primero, visita la expresión para obtener su tipo
        expr_type = self._visit(node.expression)
        if expr_type is None:  # Error en la expresión, ya reportado
            return

        # Ahora, maneja el lado izquierdo (location)
        if isinstance(node.location, IdentifierLocation):
            var_name = (
                node.location.name
            )  # Asume que name es string. Necesitaría `node.location.token`
            id_loc_node = node.location  # Para ubicación del error

            symbol = self.symbol_table.current_scope.lookup(var_name)
            if not symbol:
                self._add_error(
                    f"Asignación a variable no declarada '{var_name}'.", id_loc_node
                )
                return
            if symbol.kind == SymbolKind.CONSTANT:
                self._add_error(
                    f"No se puede asignar a la constante '{var_name}'.", id_loc_node
                )
                return
            if symbol.kind == SymbolKind.FUNCTION:
                self._add_error(
                    f"No se puede asignar a un nombre de función '{var_name}'.",
                    id_loc_node,
                )
                return

            if not self.symbol_table.is_type_assignable(symbol.type, expr_type):
                self._add_error(
                    f"No se puede asignar un valor de tipo '{expr_type}' a la variable '{var_name}' de tipo '{symbol.type}'.",
                    node.expression,
                )  # Error en la expresión
            symbol.initialized = True

        elif isinstance(node.location, DereferenceLocation):
            # `location <- '`' expression`
            # Aquí la semántica de tu lenguaje es crucial para el chequeo de tipos.
            # Si la expresión es una "dirección" (int), el tipo del valor en esa dirección es desconocido estáticamente.
            addr_expr_node = node.location.expression
            address_expr_type = self._visit(addr_expr_node)
            if (
                address_expr_type and address_expr_type != "int"
            ):  # Permitir None si hubo error en addr_expr
                self._add_error(
                    f"La expresión para desreferenciar (puntero) debe ser de tipo 'int', pero se encontró '{address_expr_type}'.",
                    addr_expr_node,
                )
            # No podemos verificar si `expr_type` es compatible con lo que hay en memoria.
            # Es una operación inherentemente insegura en cuanto a tipos sin más información.
            # print(f"Advertencia (Línea ...): Asignación a ubicación de memoria dereferenciada. El tipo del valor ('{expr_type}') no puede ser verificado estáticamente contra el tipo del destino.")
            pass  # Se permite la asignación, la seguridad de tipos es responsabilidad del programador aquí.
        else:
            self._add_error(
                "El lado izquierdo de una asignación debe ser una variable o una ubicación de memoria dereferenciada.",
                node.location,
            )

    def _visit_BinaryOp(self, node: BinaryOp):
        op_loc = node.op_token if hasattr(node, "op_token") else node

        left_type = self._visit(node.left)
        right_type = self._visit(node.right)

        if left_type is None or right_type is None:
            return None

        op_char = node.op
        result_type = self.symbol_table.get_binary_op_result_type(
            op_char, left_type, right_type
        )

        if result_type is None:
            self._add_error(
                f"Operador binario '{op_char}' no se puede aplicar a operandos de tipo '{left_type}' y '{right_type}'.",
                op_loc,
            )
            return None
        return result_type

    def _visit_UnaryOp(self, node: UnaryOp):
        op_loc = node.op_token if hasattr(node, "op_token") else node

        expr_type = self._visit(node.expr)
        if expr_type is None:
            return None

        op_char = node.op
        if (
            op_char == "NOT"
            and hasattr(node, "op_token")
            and node.op_token.value == "!"
        ):
            op_char = "!"

        result_type = self.symbol_table.get_unary_op_result_type(op_char, expr_type)
        if result_type is None:
            if op_char == "^":
                self._add_error(
                    f"Operador unario '{op_char}' (GROW) no tiene una semántica de tipos definida actualmente.",
                    op_loc,
                )
            else:
                self._add_error(
                    f"Operador unario '{op_char}' no se puede aplicar a un operando de tipo '{expr_type}'.",
                    op_loc,
                )
            return None
        return result_type

    def _visit_Literal(self, node: Literal):
        ttype = node.type_token
        if ttype == "INTEGER":
            return "int"
        if ttype == "FLOAT":
            return "float"
        if ttype == "CHAR":
            return "char"
        if ttype == "TRUE" or ttype == "FALSE":
            return "bool"

        self._add_error(f"Tipo de literal desconocido o inesperado: {ttype}", node)
        return None

    def _visit_IdentifierLocation(self, node: IdentifierLocation):
        name = node.name
        symbol = self.symbol_table.current_scope.lookup(name)

        if not symbol:
            self._add_error(f"Uso de identificador no declarado '{name}'.", node)
            return None
        if symbol.kind == SymbolKind.FUNCTION:
            self._add_error(
                f"El nombre de función '{name}' no puede ser usado como un valor directamente en este contexto.",
                node,
            )
            return None

        return symbol.type

    def _visit_DereferenceLocation(self, node: DereferenceLocation):
        addr_expr_node = node.expression
        address_expr_type = self._visit(addr_expr_node)

        if address_expr_type and address_expr_type != "int":
            self._add_error(
                f"La expresión para desreferenciar (puntero) debe ser de tipo 'int', pero se encontró '{address_expr_type}'.",
                addr_expr_node,
            )
            return None

        return "int"

    def _visit_FuncDecl(self, node: FuncDecl):
        func_name = node.identifier
        id_token_for_loc = node.id_token if hasattr(node, "id_token") else node

        if self.symbol_table.current_scope.lookup(func_name, current_scope_only=True):
            self._add_error(
                f"Función '{func_name}' ya declarada en este ámbito.", id_token_for_loc
            )

        return_type_str = node.return_type
        type_token_for_loc = (
            node.return_type_token if hasattr(node, "return_type_token") else node
        )
        if return_type_str not in self.symbol_table.valid_types:
            self._add_error(
                f"Tipo de retorno desconocido '{return_type_str}' para función '{func_name}'.",
                type_token_for_loc,
            )
            return_type_str = None

        params_info_for_symbol = []
        param_names_in_decl = set()
        if node.parameters and node.parameters.params:
            for p_idx, (p_name_str, p_type_str) in enumerate(node.parameters.params):
                param_loc_node = node.parameters
                if (
                    hasattr(node.parameters, "param_tokens")
                    and len(node.parameters.param_tokens) > p_idx
                ):
                    param_loc_node = node.parameters.param_tokens[p_idx]

                if p_name_str in param_names_in_decl:
                    self._add_error(
                        f"Parámetro '{p_name_str}' duplicado en la declaración de la función '{func_name}'.",
                        param_loc_node,
                    )
                param_names_in_decl.add(p_name_str)

                if p_type_str not in self.symbol_table.valid_types:
                    self._add_error(
                        f"Tipo de parámetro desconocido '{p_type_str}' para '{p_name_str}' en función '{func_name}'.",
                        param_loc_node,
                    )
                    params_info_for_symbol.append(
                        {"name": p_name_str, "type": None, "node": param_loc_node}
                    )
                else:
                    params_info_for_symbol.append(
                        {"name": p_name_str, "type": p_type_str, "node": param_loc_node}
                    )

        func_symbol = Symbol(
            func_name,
            SymbolKind.FUNCTION,
            sym_type=return_type_str,
            node=id_token_for_loc,
            params_info=params_info_for_symbol,
            return_type=return_type_str,
            is_import=node.is_import,
        )

        if not self.symbol_table.current_scope.lookup(
            func_name, current_scope_only=True
        ):
            self.symbol_table.current_scope.define(func_symbol)

        if node.is_import:
            return

        self.symbol_table.enter_scope(
            scope_name=f"<func_body_{func_name}>", current_function_symbol=func_symbol
        )

        for p_info in params_info_for_symbol:
            if p_info["type"]:
                param_sym = Symbol(
                    p_info["name"],
                    SymbolKind.PARAMETER,
                    p_info["type"],
                    node=p_info["node"],
                )
                if not self.symbol_table.current_scope.define(param_sym):
                    pass

        for stmt in node.body:
            self._visit(stmt)

        if (
            return_type_str
            and return_type_str != "void"
            and not func_symbol.has_return_statement
        ):
            self._add_error(
                f"Función '{func_name}' con tipo de retorno '{return_type_str}' podría no retornar un valor en todas sus rutas (o no tiene sentencia 'return').",
                id_token_for_loc,
            )

        self.symbol_table.exit_scope()

    def _visit_FunctionCall(self, node: FunctionCall):
        func_name = node.name
        call_loc_node = node.name_token if hasattr(node, "name_token") else node

        func_symbol = self.symbol_table.current_scope.lookup(func_name)

        if not func_symbol:
            self._add_error(
                f"Llamada a función no declarada '{func_name}'.", call_loc_node
            )
            return None
        if func_symbol.kind != SymbolKind.FUNCTION:
            self._add_error(
                f"'{func_name}' fue declarado como {str(func_symbol.kind).split('.')[-1].lower()} y no como función, por lo tanto no se puede llamar.",
                call_loc_node,
            )
            return None

        expected_params_info = func_symbol.params_info
        num_expected_args = len(expected_params_info)
        num_passed_args = len(node.arguments) if node.arguments else 0

        if num_passed_args != num_expected_args:
            self._add_error(
                f"Función '{func_name}' espera {num_expected_args} argumento(s), pero se pasaron {num_passed_args}.",
                call_loc_node,
            )
            return func_symbol.return_type

        for i, arg_expr_node in enumerate(node.arguments):
            passed_arg_type = self._visit(arg_expr_node)
            if passed_arg_type is None:
                continue

            expected_param_type = expected_params_info[i]["type"]
            if expected_param_type is None:
                continue

            if not self.symbol_table.is_type_assignable(
                expected_param_type, passed_arg_type
            ):
                param_name = expected_params_info[i]["name"]
                self._add_error(
                    f"Argumento '{param_name}' (posición {i+1}) en llamada a '{func_name}': se esperaba tipo '{expected_param_type}', pero se pasó tipo '{passed_arg_type}'.",
                    arg_expr_node,
                )

        return func_symbol.return_type

    def _visit_IfStmt(self, node: IfStmt):
        condition_type = self._visit(node.condition)
        if condition_type is not None and condition_type != "bool":
            self._add_error(
                f"La condición de la sentencia 'if' debe ser de tipo 'bool', pero se encontró tipo '{condition_type}'.",
                node.condition,
            )

        self.symbol_table.enter_scope(scope_name="<if_then_block>")
        for stmt in node.then_block:
            self._visit(stmt)
        self.symbol_table.exit_scope()

        if node.else_block:
            self.symbol_table.enter_scope(scope_name="<if_else_block>")
            for stmt in node.else_block:
                self._visit(stmt)
            self.symbol_table.exit_scope()

    def _visit_WhileStmt(self, node: WhileStmt):
        condition_type = self._visit(node.condition)
        if condition_type is not None and condition_type != "bool":
            self._add_error(
                f"La condición de la sentencia 'while' debe ser de tipo 'bool', pero se encontró tipo '{condition_type}'.",
                node.condition,
            )

        self.symbol_table.enter_scope(scope_name="<while_body>", is_loop=True)
        for stmt in node.body:
            self._visit(stmt)
        self.symbol_table.exit_scope()

    def _visit_BreakStmt(self, node: BreakStmt):
        if not self.symbol_table.current_scope.is_in_loop():
            self._add_error(
                "Sentencia 'break' solo permitida dentro de un bucle ('while').", node
            )

    def _visit_ContinueStmt(self, node: ContinueStmt):
        if not self.symbol_table.current_scope.is_in_loop():
            self._add_error(
                "Sentencia 'continue' solo permitida dentro de un bucle ('while').",
                node,
            )

    def _visit_ReturnStmt(self, node: ReturnStmt):
        current_func_sym = self.symbol_table.current_scope.get_current_function_symbol()

        if not current_func_sym:
            self._add_error(
                "Sentencia 'return' solo permitida dentro de una función.", node
            )
            self._visit(node.expression)
            return

        current_func_sym.has_return_statement = True

        expected_return_type = current_func_sym.return_type

        returned_expr_type = self._visit(node.expression)
        if returned_expr_type is None:
            return

        if expected_return_type is None:
            return

        if not self.symbol_table.is_type_assignable(
            expected_return_type, returned_expr_type
        ):
            self._add_error(
                f"No se puede retornar un valor de tipo '{returned_expr_type}' desde una función ('{current_func_sym.name}') con tipo de retorno declarado '{expected_return_type}'.",
                node.expression,
            )

    def _visit_PrintStmt(self, node: PrintStmt):
        expr_type = self._visit(node.expression)
        if expr_type is None:
            return

        allowed_print_types = {"int", "float", "char", "bool"}
        if expr_type not in allowed_print_types:
            self._add_error(
                f"No se puede usar 'print' directamente con un valor de tipo '{expr_type}'. Se esperan tipos básicos (int, float, char, bool).",
                node.expression,
            )

    def _visit_Cast(self, node: Cast):
        target_type_str = node.cast_type
        cast_type_loc = node.type_token if hasattr(node, "type_token") else node

        if (
            target_type_str not in self.symbol_table.valid_types
            or target_type_str == "void"
        ):
            self._add_error(
                f"Casteo a tipo inválido o no permitido '{target_type_str}'.",
                cast_type_loc,
            )
            self._visit(node.expression)
            return None

        source_expr_type = self._visit(node.expression)
        if source_expr_type is None:
            return None

        if not self.symbol_table.is_type_castable(target_type_str, source_expr_type):
            self._add_error(
                f"No se puede realizar el casteo explícito de tipo '{source_expr_type}' a tipo '{target_type_str}'.",
                node,
            )
            return None

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
