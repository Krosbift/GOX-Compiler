from prettytable import PrettyTable, ALL
from colorama import Fore, Style, init as colorama_init
from ...shared.symtable.symtable import Scope, Symbol, SymbolTable
from ...shared.symtable.symbol import Symbol, SymbolKind

colorama_init(autoreset=True)


class SymbolTablePrinter:
    def __init__(self, symbol_table: SymbolTable):
        self.symbol_table = symbol_table

    def print_table(self):
        print(Style.BRIGHT + Fore.CYAN + "=" * 70)
        print(Style.BRIGHT + Fore.CYAN + "TABLA DE SÍMBOLOS COMPLETA".center(70))
        print(Style.BRIGHT + Fore.CYAN + "=" * 70)
        self._print_scope_recursively(self.symbol_table.global_scope, 0)
        print(Style.BRIGHT + Fore.CYAN + "=" * 70)

    def _print_scope_recursively(self, scope: Scope, depth: int):
        indent_str = "  " * depth

        # Determinar el nombre del ámbito
        scope_display_name = scope.scope_name
        scope_color = Fore.YELLOW
        if scope.scope_name == "<global>":
            scope_display_name = "Ámbito Global"
            scope_color = Fore.GREEN
        elif scope.current_function_symbol:
            scope_display_name = f"Función: '{scope.current_function_symbol.name}'"
            scope_color = Fore.MAGENTA
        elif scope.scope_name == "<program_body>":  # Si usas este nombre específico
            scope_display_name = "Cuerpo del Programa Principal"
            scope_color = Fore.GREEN
        else:  # Otros bloques como if/while
            scope_display_name = f"Bloque: '{scope.scope_name}'"
            scope_color = Fore.BLUE

        print(
            f"\n{indent_str}{Style.BRIGHT}{scope_color}ÁMBITO: {scope_display_name} (Profundidad {depth})"
        )
        if scope.is_loop:
            print(f"{indent_str}{Fore.BLUE}  [BUCLE]")

        if not scope.symbols:
            print(
                f"{indent_str}{Fore.LIGHTBLACK_EX}  (Este ámbito no define símbolos directamente)"
            )
        else:
            table = PrettyTable()
            table.field_names = [
                Style.BRIGHT + "Nombre",
                Style.BRIGHT + "Categoría",
                Style.BRIGHT + "Tipo",
                Style.BRIGHT + "Info Adicional",
            ]
            table.align["Nombre"] = "l"
            table.align["Categoría"] = "l"
            table.align["Tipo"] = "l"
            table.align["Info Adicional"] = "l"

            # Aplicar estilo a los bordes (opcional, pero ALL es común)
            table.hrules = ALL

            for name, symbol in scope.symbols.items():
                s_name = symbol.name
                s_kind_str = str(symbol.kind).split(".")[-1]
                s_type_str = self._format_symbol_type(symbol)

                s_extra_parts = []
                extra_color = Fore.WHITE  # Color por defecto para info extra

                if symbol.kind == SymbolKind.FUNCTION:
                    s_kind_str = Fore.CYAN + s_kind_str
                    if symbol.is_import:
                        s_extra_parts.append(Fore.YELLOW + "importada")
                    # Chequeo de retorno (simplificado)
                    if (
                        not symbol.is_import
                        and symbol.return_type
                        and symbol.return_type != "void"
                    ):
                        if not symbol.has_return_statement:
                            s_extra_parts.append(Fore.RED + "sin return?")

                elif symbol.kind == SymbolKind.CONSTANT:
                    s_kind_str = Fore.LIGHTGREEN_EX + s_kind_str
                    # Las constantes deben ser inicializadas por definición en tu checker

                elif symbol.kind == SymbolKind.VARIABLE:
                    s_kind_str = Fore.LIGHTBLUE_EX + s_kind_str
                    if not symbol.initialized:
                        s_extra_parts.append(Fore.YELLOW + "no inicializada")

                elif symbol.kind == SymbolKind.PARAMETER:
                    s_kind_str = Fore.LIGHTMAGENTA_EX + s_kind_str
                    # Los parámetros siempre están inicializados

                s_extra_str = (
                    (Style.RESET_ALL + ", ").join(s_extra_parts)
                    if s_extra_parts
                    else Fore.LIGHTBLACK_EX + "-"
                )

                table.add_row(
                    [
                        s_name,
                        s_kind_str
                        + Style.RESET_ALL,  # Reset para que el color no se propague a la tabla
                        s_type_str,
                        s_extra_str + Style.RESET_ALL,
                    ]
                )

            # Imprimir la tabla con indentación
            table_string = table.get_string()
            indented_table_string = "\n".join(
                [f"{indent_str}  {line}" for line in table_string.splitlines()]
            )
            print(indented_table_string)

        # Recursivamente imprimir ámbitos hijos
        for child_scope in scope.children_scopes:
            self._print_scope_recursively(child_scope, depth + 1)

        # if not scope.children_scopes and scope.symbols:
        #     print("") # Quitar el espacio extra, PrettyTable ya maneja bien el espaciado

    def _format_symbol_type(self, symbol: Symbol) -> str:
        if symbol.kind == SymbolKind.FUNCTION:
            param_types_str = []
            for p_info in symbol.params_info:
                p_type = p_info["type"] or Fore.RED + "?" + Style.RESET_ALL
                param_types_str.append(p_type)

            params_formatted = (Fore.WHITE + ", ").join(param_types_str)
            return_t = (
                symbol.return_type or "void"
            )  # Asumiendo que 'void' está en tus valid_types si aplica

            # Colorear los paréntesis y la flecha
            return f"{Fore.WHITE}({params_formatted}{Fore.WHITE}) {Style.BRIGHT}{Fore.WHITE}->{Style.RESET_ALL} {Fore.GREEN}{return_t}{Style.RESET_ALL}"

        type_color_map = {
            "int": Fore.GREEN,
            "float": Fore.GREEN,
            "char": Fore.GREEN,
            "bool": Fore.GREEN,
            "void": Fore.LIGHTBLACK_EX,  # Si usas void
        }
        type_str = symbol.type or (Fore.RED + "desconocido" + Style.RESET_ALL)
        return type_color_map.get(type_str, Fore.WHITE) + type_str + Style.RESET_ALL
