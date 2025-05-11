from .symbol import Symbol


class Scope:
    def __init__(
        self,
        parent_scope=None,
        scope_name="<unnamed_scope>",
        is_loop=False,
        current_function_symbol=None,
    ):
        self.symbols = {}
        self.parent_scope = parent_scope
        self.scope_name = scope_name
        self.is_loop = is_loop
        self.current_function_symbol = current_function_symbol
        self.children_scopes = []
        if parent_scope:
            parent_scope.children_scopes.append(self)

    def define(self, symbol: Symbol):
        if symbol.name in self.symbols:
            return False
        self.symbols[symbol.name] = symbol
        return True

    def lookup(self, name: str, current_scope_only=False) -> Symbol | None:
        if name in self.symbols:
            return self.symbols[name]
        if not current_scope_only and self.parent_scope:
            return self.parent_scope.lookup(name)
        return None

    def is_in_loop(self) -> bool:
        if self.is_loop:
            return True
        if self.parent_scope:
            return self.parent_scope.is_in_loop()
        return False

    def get_current_function_symbol(self) -> Symbol | None:
        if self.current_function_symbol:
            return self.current_function_symbol
        if self.parent_scope:
            return self.parent_scope.get_current_function_symbol()
        return None


class SymbolTable:
    def __init__(self):
        self.global_scope = Scope(scope_name="<global>")
        self.current_scope = self.global_scope
        self.valid_types = {
            "int",
            "float",
            "char",
            "bool",
            "void",
        }

        self.type_compatibility_rules = {
            # Aritméticos
            ("+", "int", "int"): "int",
            ("+", "float", "float"): "float",
            ("-", "int", "int"): "int",
            ("-", "float", "float"): "float",
            ("*", "int", "int"): "int",
            ("*", "float", "float"): "float",
            (
                "/",
                "int",
                "int",
            ): "int",  # Podría ser float si la división de enteros resulta en float
            ("/", "float", "float"): "float",
            # Comparaciones (devuelven bool)
            ("==", "int", "int"): "bool",
            ("!=", "int", "int"): "bool",
            ("==", "float", "float"): "bool",
            ("!=", "float", "float"): "bool",
            ("==", "char", "char"): "bool",
            ("!=", "char", "char"): "bool",
            ("==", "bool", "bool"): "bool",
            ("!=", "bool", "bool"): "bool",
            ("<", "int", "int"): "bool",
            (">", "int", "int"): "bool",
            ("<=", "int", "int"): "bool",
            (">=", "int", "int"): "bool",
            ("<", "float", "float"): "bool",
            (">", "float", "float"): "bool",
            ("<=", "float", "float"): "bool",
            (">=", "float", "float"): "bool",
            # Lógicos
            ("&&", "bool", "bool"): "bool",
            ("||", "bool", "bool"): "bool",
        }
        # (op, type) -> result_type
        self.unary_op_type_compatibility = {
            ("+", "int"): "int",
            ("+", "float"): "float",
            ("-", "int"): "int",
            ("-", "float"): "float",
            ("!", "bool"): "bool",  # NOT lógico
            # '^' para tu gramática era 'GROW'. Asumiré que es un operador unario no estándar.
            # Si es exponenciación, usualmente es binario. Si es NOT bit a bit, aplica a int.
            # Por ahora lo omito hasta que se aclare su semántica. Si es un error, mejor.
        }

    def enter_scope(
        self, scope_name="<block>", is_loop=False, current_function_symbol=None
    ):
        if current_function_symbol is None and self.current_scope:
            current_function_symbol = self.current_scope.get_current_function_symbol()

        new_scope = Scope(
            parent_scope=self.current_scope,
            scope_name=scope_name,
            is_loop=is_loop,
            current_function_symbol=current_function_symbol,
        )
        self.current_scope = new_scope

    def exit_scope(self):
        if self.current_scope.parent_scope:
            self.current_scope = self.current_scope.parent_scope
        else:
            # Este error no debería ocurrir si el checker maneja bien los scopes.
            raise Exception("InternalError: Cannot exit global scope")

    def _normalize_type_name(self, type_name_from_ast):
        # Esto es para mapear los nombres de TIPO DE TOKEN de tu lexer a los nombres de tipo internos
        # Asumo que tus nodos AST ya usan 'int', 'float', etc. directamente para var_type.
        # Si vienen de tokens como 'INT_TYPE', 'FLOAT_TYPE', necesitarías mapearlos aquí.
        # Ejemplo: if type_name_from_ast == 'INT_TYPE': return 'int'
        if type_name_from_ast == "FLOAT_TYPE":
            return "float"  # De tu gramática de tokens
        if type_name_from_ast == "CHAR_TYPE":
            return "char"  # De tu gramática de tokens
        # 'INT', 'BOOL' de la gramática de tokens para tipos ya son 'int', 'bool'.
        return type_name_from_ast

    def get_binary_op_result_type(
        self, op: str, left_type: str, right_type: str
    ) -> str | None:
        left_type_norm = self._normalize_type_name(left_type)
        right_type_norm = self._normalize_type_name(right_type)

        # Intento directo
        if (op, left_type_norm, right_type_norm) in self.type_compatibility_rules:
            return self.type_compatibility_rules[(op, left_type_norm, right_type_norm)]

        # Coerción implícita: int a float si el otro es float (para operadores aritméticos y comparativos)
        arithmetic_comparison_ops = {
            "+",
            "-",
            "*",
            "/",
            "<",
            ">",
            "<=",
            ">=",
            "==",
            "!=",
        }
        if op in arithmetic_comparison_ops:
            if left_type_norm == "int" and right_type_norm == "float":
                if (op, "float", "float") in self.type_compatibility_rules:
                    return self.type_compatibility_rules[(op, "float", "float")]
            if left_type_norm == "float" and right_type_norm == "int":
                if (op, "float", "float") in self.type_compatibility_rules:
                    return self.type_compatibility_rules[(op, "float", "float")]
        return None

    def get_unary_op_result_type(self, op: str, expr_type: str) -> str | None:
        expr_type_norm = self._normalize_type_name(expr_type)
        if (op, expr_type_norm) in self.unary_op_type_compatibility:
            return self.unary_op_type_compatibility[(op, expr_type_norm)]
        return None

    def is_type_assignable(self, target_type: str, value_type: str) -> bool:
        target_type_norm = self._normalize_type_name(target_type)
        value_type_norm = self._normalize_type_name(value_type)

        if target_type_norm == value_type_norm:
            return True
        # Coerción implícita: se puede asignar un int a un float
        if target_type_norm == "float" and value_type_norm == "int":
            return True
        return False

    def is_type_castable(self, cast_to_type: str, cast_from_type: str) -> bool:
        cast_to_norm = self._normalize_type_name(cast_to_type)
        cast_from_norm = self._normalize_type_name(cast_from_type)

        if (
            cast_to_norm not in self.valid_types
            or cast_from_norm not in self.valid_types
        ):
            return (
                False  # Uno de los tipos no es válido (excluyendo 'void' para casteo)
            )
        if (
            cast_to_norm == "void" or cast_from_norm == "void"
        ):  # No se puede castear a/desde void
            return False

        # Mismas reglas que asignación
        if self.is_type_assignable(cast_to_norm, cast_from_norm):
            return True

        # Casos adicionales de casteo (ej. float a int - truncamiento)
        if cast_to_norm == "int" and cast_from_norm == "float":
            return True

        # Permitir cualquier cast entre tipos numéricos y char (interpretación ASCII/valor)
        numeric_char_types = {"int", "float", "char"}
        if cast_to_norm in numeric_char_types and cast_from_norm in numeric_char_types:
            return True

        # bool a int/float (true=1, false=0)
        if cast_to_norm in ("int", "float") and cast_from_norm == "bool":
            return True
        # int/float a bool (0=false, no-cero=true)
        if cast_to_norm == "bool" and cast_from_norm in ("int", "float"):
            return True

        return False
