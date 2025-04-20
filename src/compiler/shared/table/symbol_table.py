# semantic/symbol_table.py
from collections import OrderedDict
from prettytable import PrettyTable
from colorama import Fore, Style, init

init(autoreset=True)  # Inicializa colorama


class Symbol:
    """Representa una entrada en la tabla de símbolos."""

    def __init__(
        self,
        name,
        kind,
        type,
        scope_level,
        is_mutable=True,
        initialized=False,
        node=None,
    ):
        self.name = name
        self.kind = kind  # 'var', 'const', 'func', 'param'
        self.type = type  # 'int', 'float', 'bool', 'char', o una tupla para funciones ('func', (param_types,), return_type)
        self.scope_level = scope_level
        self.is_mutable = is_mutable
        self.initialized = (
            initialized  # Útil para detectar variables usadas antes de asignarles valor
        )
        self.node = node  # Referencia al nodo AST (opcional, útil para errores)
        # Para funciones:
        self.param_types = None
        self.return_type = None
        if isinstance(type, tuple) and type[0] == "func":
            _, self.param_types, self.return_type = type

    def __str__(self):
        type_str = self._format_type(self.type)
        mutability = "Mutable" if self.is_mutable else "Immutable"
        return f"Symbol(name='{self.name}', kind='{self.kind}', type='{type_str}', scope={self.scope_level}, mutability='{mutability}')"

    def _format_type(self, type_obj):
        if isinstance(type_obj, tuple) and type_obj[0] == "func":
            _, params, ret = type_obj
            param_str = (
                ", ".join(self._format_type(p) for p in params) if params else ""
            )
            ret_str = self._format_type(ret)
            return f"func({param_str}) -> {ret_str}"
        elif isinstance(type_obj, str):
            # Mapeo simple de tipos internos a nombres más legibles si es necesario
            type_map = {
                "INT": "int",
                "INTEGER": "int",
                "FLOAT_TYPE": "float",
                "FLOAT": "float",
                "CHAR_TYPE": "char",
                "CHAR": "char",
                "BOOL": "bool",
                "TRUE": "bool",
                "FALSE": "bool",
            }
            return type_map.get(
                type_obj.upper(), type_obj
            )  # Devuelve el tipo mapeado o el original
        return str(type_obj)  # Fallback


class Scope:
    """Representa un nivel de alcance (scope)."""

    def __init__(self, level, enclosing_scope=None):
        self.level = level
        self.symbols = (
            OrderedDict()
        )  # Usamos OrderedDict para mantener el orden de declaración
        self.enclosing_scope = enclosing_scope

    def define(self, symbol: Symbol):
        """Define un símbolo en este scope."""
        if symbol.name in self.symbols:
            return False  # Ya existe en este scope
        self.symbols[symbol.name] = symbol
        return True

    def resolve(self, name: str, current_scope_only=False):
        """Busca un símbolo por nombre, empezando desde este scope hacia afuera."""
        symbol = self.symbols.get(name)
        if symbol:
            return symbol
        if not current_scope_only and self.enclosing_scope:
            return self.enclosing_scope.resolve(name)
        return None

    def __str__(self):
        return f"Scope(level={self.level}, symbols={list(self.symbols.keys())})"


class SymbolTable:
    """Gestiona los scopes y la tabla de símbolos completa."""

    def __init__(self):
        self.current_scope = Scope(level=0)  # Scope global
        self.scope_stack = [self.current_scope]
        self._all_symbols_in_order = []  # Para mantener el orden global de definicion

    def enter_scope(self):
        """Entra en un nuevo scope anidado."""
        new_level = self.current_scope.level + 1
        new_scope = Scope(level=new_level, enclosing_scope=self.current_scope)
        self.scope_stack.append(new_scope)
        self.current_scope = new_scope
        # print(f"Entered Scope Level: {self.current_scope.level}") # Debug

    def exit_scope(self):
        """Sale del scope actual."""
        if self.current_scope.level > 0:
            # print(f"Exiting Scope Level: {self.current_scope.level}") # Debug
            self.scope_stack.pop()
            self.current_scope = self.scope_stack[-1]
        else:
            # print("Warning: Attempted to exit global scope.") # Debug
            pass  # No salir del scope global

    def define(self, symbol: Symbol):
        """Define un símbolo en el scope actual."""
        symbol.scope_level = (
            self.current_scope.level
        )  # Asegura que el nivel es correcto
        if not self.current_scope.define(symbol):
            # Error: Símbolo ya definido en este scope
            return (
                False,
                f"Error: Redeclaración del símbolo '{symbol.name}' en el mismo scope (nivel {self.current_scope.level}).",
            )
        self._all_symbols_in_order.append(symbol)  # Añadir al orden global
        return True, None  # Éxito

    def resolve(self, name: str):
        """Busca un símbolo empezando desde el scope actual hacia afuera."""
        return self.current_scope.resolve(name)

    def resolve_current_scope(self, name: str):
        """Busca un símbolo sólo en el scope actual."""
        return self.current_scope.resolve(name, current_scope_only=True)

    def print_table(self):
        """Imprime la tabla de símbolos de forma bonita usando PrettyTable."""
        if not self._all_symbols_in_order:
            print(Fore.YELLOW + "La tabla de símbolos está vacía.")
            return

        table = PrettyTable()
        table.field_names = [
            Fore.CYAN + "Name",
            Fore.CYAN + "Kind",
            Fore.CYAN + "Type",
            Fore.CYAN + "Scope Level",
            Fore.CYAN + "Mutability" + Style.RESET_ALL,
        ]
        table.align = "l"

        for symbol in self._all_symbols_in_order:
            type_str = symbol._format_type(
                symbol.type
            )  # Usar el formateador del símbolo
            mutability = (
                Fore.GREEN + "Mutable" if symbol.is_mutable else Fore.RED + "Immutable"
            )

            table.add_row(
                [
                    Fore.WHITE + symbol.name,
                    Fore.YELLOW + symbol.kind,
                    Fore.MAGENTA + type_str,
                    Fore.BLUE + str(symbol.scope_level),
                    mutability + Style.RESET_ALL,
                ]
            )

        print("\n" + Fore.GREEN + "===== TABLA DE SÍMBOLOS =====" + Style.RESET_ALL)
        print(table)
        print(Fore.GREEN + "=============================" + Style.RESET_ALL + "\n")
