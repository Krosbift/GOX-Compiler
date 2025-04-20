from ..shared.table.symbol_table import SymbolTable, Symbol
from .errors.senser import (
    SemanticError,
    TypeMismatchError,
    UndeclaredIdentifierError,
    RedeclarationError,
    AssignmentError,
    FunctionError,
    ScopeError,
)
from ..shared.table.types import (
    TYPE_INT,
    TYPE_FLOAT,
    TYPE_BOOL,
    TYPE_CHAR,
    TYPE_VOID,
    TYPE_ERROR,
    get_type_from_name,
    is_numeric,
    is_boolean,
    is_compatible_for_assignment,
    check_binary_op_type,
    check_unary_op_type,
)
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


class Senser:
    def __init__(self):
        self.symbol_table = SymbolTable()
        self.errors = []
        self.current_function_return_type = None  # Para verificar retornos
        self.loop_level = 0  # Para verificar break/continue

    def add_error(self, error: SemanticError):
        self.errors.append(error)
        # print(f"DEBUG: Error added: {error}") # Para depuración

    def visit(self, node):
        """Método de visita genérico que despacha al método específico."""
        method_name = f"visit_{type(node).__name__}"
        visitor = getattr(self, method_name, self.generic_visit)
        # print(f"Visiting: {type(node).__name__}") # Debug
        return visitor(node)

    def generic_visit(self, node):
        """Visita genérica para nodos sin un método específico (si es necesario)."""
        # print(f"Warning: No specific visitor for {type(node).__name__}")
        # Podrías intentar visitar hijos genéricamente, pero es propenso a errores.
        # Es mejor asegurarse de tener un visitor para cada nodo AST relevante.
        return None  # O algún valor por defecto

    def analyze(self, ast_root: Program):
        """Punto de entrada para iniciar el análisis semántico."""
        self.errors = []
        self.current_function_return_type = None
        self.loop_level = 0
        try:
            self.visit(ast_root)
        except SemanticError as e:
            # Captura errores lanzados directamente si es necesario
            self.add_error(e)
        except Exception as e:
            # Captura errores inesperados durante el análisis
            self.add_error(SemanticError(f"Error interno del Senser: {e}"))
            import traceback

            traceback.print_exc()  # Imprime el stack trace para depuración

        print("\n--- Análisis Semántico Completado ---")
        if self.errors:
            print(f"{len(self.errors)} Errores Semánticos Encontrados:")
            for error in self.errors:
                print(f"- {error}")
        else:
            print("No se encontraron errores semánticos.")

        # Imprimir la tabla de símbolos al final
        self.symbol_table.print_table()

        return not self.errors  # Retorna True si no hubo errores, False si los hubo

    # --- Visitors para cada tipo de nodo AST ---

    def visit_Program(self, node: Program):
        # Podrías agregar símbolos predefinidos aquí si tu lenguaje los tiene (ej: print, read)
        # self.symbol_table.define(Symbol('print', 'func', ...))

        for statement in node.statements:
            self.visit(statement)

    def visit_VarDecl(self, node: VarDecl):
        var_name = node.identifier
        declared_type = get_type_from_name(node.var_type) if node.var_type else None
        is_const = node.kind == "CONST"
        initializer_type = None

        # Verificar si ya existe en el scope ACTUAL
        if self.symbol_table.resolve_current_scope(var_name):
            self.add_error(
                RedeclarationError(
                    f"Variable '{var_name}' ya declarada en este scope.", node
                )
            )
            # Aún así, intentamos continuar definiéndola para minimizar errores cascada,
            # pero marcándola como errónea internamente si fuera necesario.
            effective_type = TYPE_ERROR
        else:
            effective_type = declared_type  # Tipo inicial

        # Procesar inicializador si existe
        if node.initializer:
            initializer_type = self.visit(node.initializer)
            if initializer_type == TYPE_ERROR:
                # Si el inicializador tiene error, propagamos el error
                effective_type = TYPE_ERROR
            elif declared_type:
                # Si hay tipo declarado Y inicializador, verificar compatibilidad
                if not is_compatible_for_assignment(declared_type, initializer_type):
                    self.add_error(
                        TypeMismatchError(
                            f"No se puede inicializar la variable '{var_name}' de tipo '{declared_type}' "
                            f"con un valor de tipo '{initializer_type}'.",
                            node.initializer,
                        )
                    )
                    effective_type = TYPE_ERROR
                else:
                    # Tipo declarado tiene precedencia
                    effective_type = declared_type
            else:
                # No hay tipo declarado, inferir del inicializador
                effective_type = initializer_type
        elif not declared_type:
            # Error: ni tipo declarado ni inicializador (a menos que tu lenguaje lo permita)
            self.add_error(
                SemanticError(
                    f"La declaración de '{var_name}' necesita un tipo o un inicializador.",
                    node,
                )
            )
            effective_type = TYPE_ERROR
        elif is_const:
            # Error: constante debe ser inicializada
            self.add_error(
                AssignmentError(
                    f"La constante '{var_name}' debe ser inicializada en su declaración.",
                    node,
                )
            )
            effective_type = TYPE_ERROR  # Podría ser el tipo declarado, pero la falta de init es error

        # Si después de todo, no tenemos un tipo válido, es un error
        if effective_type is None or effective_type == TYPE_ERROR:
            effective_type = TYPE_ERROR  # Asegura que quede marcado como error

        # Definir el símbolo en la tabla
        symbol = Symbol(
            name=var_name,
            kind="const" if is_const else "var",
            type=effective_type,
            scope_level=self.symbol_table.current_scope.level,  # Se asignará correctamente en define
            is_mutable=not is_const,
            initialized=bool(node.initializer),
            node=node,
        )
        success, error_msg = self.symbol_table.define(symbol)
        if not success:
            # Este error es redundante si ya detectamos redeclaración antes,
            # pero lo dejamos por si acaso SymbolTable tiene lógica adicional.
            # self.add_error(RedeclarationError(error_msg, node))
            pass

    def visit_Assignment(self, node: Assignment):
        # Visita la parte izquierda (location) para obtener su tipo y verificar si es asignable
        location_node = node.location
        location_type = self.visit(
            location_node
        )  # visit_IdentifierLocation o visit_DereferenceLocation

        if location_type == TYPE_ERROR:
            return  # Error ya reportado al visitar la location

        # Verificar si la location es asignable (l-value)
        symbol = None
        is_assignable = False
        if isinstance(location_node, IdentifierLocation):
            symbol = self.symbol_table.resolve(location_node.name)
            if symbol:
                if symbol.kind in [
                    "var",
                    "param",
                ]:  # Solo variables y parámetros son asignables
                    if not symbol.is_mutable:
                        self.add_error(
                            AssignmentError(
                                f"No se puede asignar a la constante '{symbol.name}'.",
                                node,
                            )
                        )
                    else:
                        is_assignable = True
                elif symbol.kind == "const":
                    self.add_error(
                        AssignmentError(
                            f"No se puede asignar a la constante '{symbol.name}'.", node
                        )
                    )
                else:  # Funciones, etc. no son l-values
                    self.add_error(
                        AssignmentError(
                            f"El identificador '{location_node.name}' no es una variable asignable.",
                            node,
                        )
                    )
            else:
                # Error de identificador no declarado ya fue (o debió ser) reportado por visit_IdentifierLocation
                pass
        elif isinstance(location_node, DereferenceLocation):
            # Si soportaras punteros, aquí verificarías si el resultado de la dereferencia es un l-value
            # Por ahora, asumimos que sí si la visita no dio error.
            # ¡Necesitarías una semántica clara para punteros!
            # self.add_error(SemanticError("La asignación a través de dereferencia no está completamente implementada.", node))
            is_assignable = True  # Asunción temporal
        else:
            self.add_error(
                AssignmentError(
                    "La parte izquierda de la asignación no es válida (no es una variable o location modificable).",
                    node,
                )
            )

        # Visita la parte derecha (expresión) para obtener su tipo
        expr_type = self.visit(node.expression)

        if expr_type == TYPE_ERROR:
            return  # Error ya reportado al visitar la expresión

        # Verificar compatibilidad de tipos si la location era asignable
        if is_assignable:
            if not is_compatible_for_assignment(location_type, expr_type):
                loc_name = (
                    location_node.name
                    if isinstance(location_node, IdentifierLocation)
                    else f"`(...)"
                )
                self.add_error(
                    TypeMismatchError(
                        f"No se puede asignar un valor de tipo '{expr_type}' a la variable '{loc_name}' de tipo '{location_type}'.",
                        node.expression,
                    )
                )
            elif symbol:  # Si es una variable directa, marcarla como inicializada
                symbol.initialized = True

    def visit_IdentifierLocation(self, node: IdentifierLocation):
        name = node.name
        symbol = self.symbol_table.resolve(name)
        if not symbol:
            self.add_error(
                UndeclaredIdentifierError(
                    f"Variable o identificador '{name}' no declarado.", node
                )
            )
            node.type = TYPE_ERROR  # Anotar el nodo con tipo error
            return TYPE_ERROR
        elif symbol.kind == "func":
            self.add_error(
                SemanticError(
                    f"No se puede usar el nombre de la función '{name}' como una variable.",
                    node,
                )
            )
            node.type = TYPE_ERROR
            return TYPE_ERROR
        # else: # Podrías añadir chequeo de 'initialized' aquí si tu lenguaje lo requiere antes de usar

        # Anotar el nodo con su tipo para uso posterior (ej. en asignación)
        node.type = symbol.type
        return symbol.type

    def visit_DereferenceLocation(self, node: DereferenceLocation):
        # Esta parte DEPENDE CRUCIALMENTE de cómo manejes los punteros/referencias.
        # Si `^` crea un tipo `Pointer(T)` y `` ` `` lo dereferencia.
        # Aquí necesitarías visitar node.expr, verificar que su tipo es `Pointer(T)`
        # y devolver `T`.
        # Como no está definido, devolvemos error o un tipo genérico.
        self.add_error(
            SemanticError(
                "La dereferencia (` `) no tiene una semántica de tipos definida.", node
            )
        )
        node.type = TYPE_ERROR
        return TYPE_ERROR

    def visit_Literal(self, node: Literal):
        literal_type_map = {
            "INTEGER": TYPE_INT,
            "FLOAT": TYPE_FLOAT,
            "CHAR": TYPE_CHAR,
            "TRUE": TYPE_BOOL,
            "FALSE": TYPE_BOOL,
        }
        node_type = literal_type_map.get(node.literal_type.upper())
        if node_type is None:
            self.add_error(
                SemanticError(f"Tipo de literal desconocido: {node.literal_type}", node)
            )
            node.type = TYPE_ERROR
            return TYPE_ERROR
        node.type = node_type  # Anotar el nodo
        return node_type

    def visit_BinaryOp(self, node: BinaryOp):
        left_type = self.visit(node.left)
        right_type = self.visit(node.right)

        if left_type == TYPE_ERROR or right_type == TYPE_ERROR:
            node.type = TYPE_ERROR
            return TYPE_ERROR

        result_type = check_binary_op_type(node.op, left_type, right_type)

        if result_type == TYPE_ERROR:
            op_map = {
                "&&": "AND lógico",
                "||": "OR lógico",
                "==": "igualdad",
                "!=": "diferencia",
                "<": "menor que",
                ">": "mayor que",
                "<=": "menor o igual",
                ">=": "mayor o igual",
                "+": "suma",
                "-": "resta",
                "*": "multiplicación",
                "/": "división",
                "^": "operador ^",
            }
            op_name = op_map.get(node.op, f"operador '{node.op}'")
            self.add_error(
                TypeMismatchError(
                    f"Operación inválida: No se puede aplicar {op_name} "
                    f"entre los tipos '{left_type}' y '{right_type}'.",
                    node,
                )
            )
            node.type = TYPE_ERROR
            return TYPE_ERROR

        node.type = result_type  # Anotar el nodo
        return result_type

    def visit_UnaryOp(self, node: UnaryOp):
        expr_type = self.visit(node.expr)

        if expr_type == TYPE_ERROR:
            node.type = TYPE_ERROR
            return TYPE_ERROR

        result_type = check_unary_op_type(node.op, expr_type)

        if result_type == TYPE_ERROR:
            # Aclarar qué hace el operador unario '^' (GROW) si aplica
            op_map = {
                "-": "negación aritmética",
                "+": "más unario",
                "^": "operador ^ unario",
            }
            op_name = op_map.get(node.op, f"operador unario '{node.op}'")

            self.add_error(
                TypeMismatchError(
                    f"Operación inválida: No se puede aplicar {op_name} "
                    f"al tipo '{expr_type}'.",
                    node,
                )
            )
            node.type = TYPE_ERROR
            return TYPE_ERROR

        node.type = result_type  # Anotar el nodo
        return result_type

    def visit_Cast(self, node: Cast):
        expr_type = self.visit(node.expr)
        target_type = get_type_from_name(node.cast_type)

        if expr_type == TYPE_ERROR:
            node.type = TYPE_ERROR
            return TYPE_ERROR

        # Aquí defines las reglas de casteo explícito permitidas
        allowed = False
        if is_numeric(expr_type) and is_numeric(target_type):
            allowed = True  # Permitir casteo entre int/float
        elif expr_type == TYPE_CHAR and target_type == TYPE_INT:
            allowed = True  # Permitir char a int (valor ASCII)
        elif expr_type == TYPE_INT and target_type == TYPE_CHAR:
            allowed = True  # Permitir int a char (truncado/módulo?)
        # Añade más reglas según tu lenguaje (ej: bool a int?)

        if not allowed:
            self.add_error(
                TypeMismatchError(
                    f"Casteo inválido: No se puede convertir explícitamente "
                    f"de tipo '{expr_type}' a '{target_type}'.",
                    node,
                )
            )
            node.type = TYPE_ERROR
            return TYPE_ERROR

        node.type = target_type  # El tipo del nodo Cast es el tipo objetivo
        return target_type

    def visit_FuncDecl(self, node: FuncDecl):
        func_name = node.identifier
        return_type = (
            get_type_from_name(node.return_type) if node.return_type else TYPE_VOID
        )  # Asume void si no hay tipo de retorno

        # Procesar tipos de parámetros ANTES de definir la función (para construir la signatura)
        param_types = []
        param_names = set()
        if node.parameters and node.parameters.params:
            for p_name, p_type_name in node.parameters.params:
                if p_name in param_names:
                    # Error de nombre de parámetro duplicado (dentro de la misma función)
                    self.add_error(
                        RedeclarationError(
                            f"Nombre de parámetro duplicado '{p_name}' en la función '{func_name}'.",
                            node,
                        )
                    )
                    # Usamos TYPE_ERROR para la signatura si hay duplicados? O solo reportamos?
                    # Por simplicidad, reportamos y continuamos con el tipo declarado.
                param_names.add(p_name)
                param_types.append(get_type_from_name(p_type_name))

        # Crear la signatura de tipo para la función
        func_type_signature = ("func", tuple(param_types), return_type)

        # Intentar definir la función en el scope actual (antes de entrar al scope de la función)
        func_symbol = Symbol(
            name=func_name,
            kind="func",
            type=func_type_signature,
            scope_level=self.symbol_table.current_scope.level,  # Se ajustará en define
            is_mutable=False,  # Las funciones no son mutables
            initialized=True,  # Se considera 'inicializada' al declararla
            node=node,
        )
        success, error_msg = self.symbol_table.define(func_symbol)
        if not success:
            self.add_error(
                RedeclarationError(
                    f"Redeclaración de la función o símbolo '{func_name}'. {error_msg or ''}",
                    node,
                )
            )
            # Si hay redeclaración, podríamos no entrar al scope o manejarlo de otra forma
            # Por ahora, continuamos pero la función podría no ser usable correctamente.

        # --- Entrar al Scope de la Función ---
        self.symbol_table.enter_scope()
        previous_function_return_type = self.current_function_return_type
        self.current_function_return_type = (
            return_type  # Guardar para verificar returns
        )

        # Definir los parámetros dentro del nuevo scope
        if node.parameters and node.parameters.params:
            # Re-iteramos para definir los símbolos de parámetros
            param_name_check = (
                set()
            )  # Para evitar doble error si ya reportamos duplicado arriba
            for i, (p_name, p_type_name) in enumerate(node.parameters.params):
                if p_name not in param_name_check:
                    param_type = param_types[i]  # Usamos el tipo ya procesado
                    param_symbol = Symbol(
                        name=p_name,
                        kind="param",
                        type=param_type,
                        scope_level=self.symbol_table.current_scope.level,
                        is_mutable=True,  # Parámetros suelen ser mutables dentro de la función
                        initialized=True,  # Se consideran inicializados al recibir valor
                        node=node,  # O un nodo específico para el parámetro si lo tuvieras
                    )
                    p_success, p_error_msg = self.symbol_table.define(param_symbol)
                    if (
                        not p_success and p_name not in param_names
                    ):  # Evita reportar de nuevo si ya se hizo por duplicado
                        self.add_error(
                            RedeclarationError(
                                f"Error al definir parámetro '{p_name}'. {p_error_msg or ''}",
                                node,
                            )
                        )
                    param_name_check.add(p_name)

        # Visitar el cuerpo de la función (si no es importada)
        # Nota: Tu parser no parece tener una forma de marcar funciones 'import' sin cuerpo.
        # Asumimos que todas las FuncDecl tienen 'body'. Si no, añade un chequeo.
        # if not node.is_import: # Si tuvieras un flag is_import
        for statement in node.body:
            self.visit(statement)

        # --- Salir del Scope de la Función ---
        self.symbol_table.exit_scope()
        self.current_function_return_type = (
            previous_function_return_type  # Restaurar el contexto anterior
        )

    def visit_FunctionCall(self, node: FunctionCall):
        func_name = node.name
        func_symbol = self.symbol_table.resolve(func_name)

        if not func_symbol:
            self.add_error(
                UndeclaredIdentifierError(
                    f"Llamada a función no declarada '{func_name}'.", node
                )
            )
            node.type = TYPE_ERROR
            return TYPE_ERROR
        elif func_symbol.kind != "func":
            self.add_error(
                SemanticError(
                    f"'{func_name}' no es una función, es un '{func_symbol.kind}'.",
                    node,
                )
            )
            node.type = TYPE_ERROR
            return TYPE_ERROR

        # Verificar número de argumentos
        expected_param_count = (
            len(func_symbol.param_types) if func_symbol.param_types else 0
        )
        actual_arg_count = len(node.args)

        if expected_param_count != actual_arg_count:
            self.add_error(
                FunctionError(
                    f"La función '{func_name}' esperaba {expected_param_count} argumento(s), pero recibió {actual_arg_count}.",
                    node,
                )
            )
            # Continuar verificando tipos de los argumentos que sí coinciden puede ser útil
            # o podemos parar aquí. Por simplicidad, paramos la verificación de tipos.
            node.type = TYPE_ERROR
            return TYPE_ERROR

        # Verificar tipos de argumentos
        arg_types = []
        types_ok = True
        for i, arg_expr in enumerate(node.args):
            arg_type = self.visit(arg_expr)
            arg_types.append(arg_type)
            expected_param_type = func_symbol.param_types[i]

            if arg_type != TYPE_ERROR and not is_compatible_for_assignment(
                expected_param_type, arg_type
            ):
                self.add_error(
                    TypeMismatchError(
                        f"Argumento {i+1} inválido para la función '{func_name}'. "
                        f"Se esperaba tipo '{expected_param_type}', pero se pasó tipo '{arg_type}'.",
                        arg_expr,
                    )
                )
                types_ok = False

        # Si hubo errores de tipo o número de args, el tipo de la llamada es error
        if not types_ok:
            node.type = TYPE_ERROR
            return TYPE_ERROR

        # Si todo está bien, el tipo de la llamada es el tipo de retorno de la función
        node.type = func_symbol.return_type
        return func_symbol.return_type

    def visit_ReturnStmt(self, node: ReturnStmt):
        if self.current_function_return_type is None:
            self.add_error(
                ScopeError("Declaración 'return' fuera de una función.", node)
            )
            return

        expected_return_type = self.current_function_return_type
        actual_return_type = self.visit(node.expression)

        if actual_return_type == TYPE_ERROR:
            return  # Error ya reportado en la expresión

        # Caso especial: función void (no debería retornar valor, o retornar sin expresión)
        # Tu parser siempre espera una expresión en ReturnStmt, así que no cubrimos `return;`
        if expected_return_type == TYPE_VOID:
            # Tu gramática fuerza una expresión, así que esto siempre sería un error si la func es void
            self.add_error(
                FunctionError(
                    f"Una función con tipo de retorno '{TYPE_VOID}' no puede retornar un valor (se encontró tipo '{actual_return_type}').",
                    node.expression,
                )
            )
        # Caso normal: verificar compatibilidad
        elif not is_compatible_for_assignment(expected_return_type, actual_return_type):
            self.add_error(
                TypeMismatchError(
                    f"Tipo de retorno inválido. Se esperaba '{expected_return_type}', "
                    f"pero la función retorna un valor de tipo '{actual_return_type}'.",
                    node.expression,
                )
            )

    def visit_IfStmt(self, node: IfStmt):
        condition_type = self.visit(node.condition)

        if condition_type != TYPE_ERROR and condition_type != TYPE_BOOL:
            self.add_error(
                TypeMismatchError(
                    f"La condición del 'if' debe ser de tipo '{TYPE_BOOL}', pero se encontró '{condition_type}'.",
                    node.condition,
                )
            )

        # Visitar bloque 'then' en un nuevo scope
        self.symbol_table.enter_scope()
        for statement in node.then_block:
            self.visit(statement)
        self.symbol_table.exit_scope()

        # Visitar bloque 'else' (si existe) en su propio nuevo scope
        if node.else_block:
            self.symbol_table.enter_scope()
            for statement in node.else_block:
                self.visit(statement)
            self.symbol_table.exit_scope()

    def visit_WhileStmt(self, node: WhileStmt):
        condition_type = self.visit(node.condition)

        if condition_type != TYPE_ERROR and condition_type != TYPE_BOOL:
            self.add_error(
                TypeMismatchError(
                    f"La condición del 'while' debe ser de tipo '{TYPE_BOOL}', pero se encontró '{condition_type}'.",
                    node.condition,
                )
            )

        # Entrar en el contexto del bucle y en un nuevo scope
        self.loop_level += 1
        self.symbol_table.enter_scope()

        for statement in node.body:
            self.visit(statement)

        # Salir del scope y del contexto del bucle
        self.symbol_table.exit_scope()
        self.loop_level -= 1

    def visit_BreakStmt(self, node: BreakStmt):
        if self.loop_level <= 0:
            self.add_error(
                ScopeError("Declaración 'break' fuera de un bucle ('while').", node)
            )

    def visit_ContinueStmt(self, node: ContinueStmt):
        if self.loop_level <= 0:
            self.add_error(
                ScopeError("Declaración 'continue' fuera de un bucle ('while').", node)
            )

    def visit_PrintStmt(self, node: PrintStmt):
        # Simplemente visita la expresión. Asumimos que 'print' puede manejar cualquier tipo básico.
        # Podrías añadir restricciones si 'print' solo acepta ciertos tipos.
        expr_type = self.visit(node.expression)
        if expr_type == TYPE_ERROR:
            pass  # Error ya reportado
        elif expr_type == TYPE_VOID:  # No se puede imprimir 'void'
            self.add_error(
                TypeMismatchError(
                    f"No se puede usar 'print' con una expresión de tipo '{TYPE_VOID}'.",
                    node.expression,
                )
            )

    # --- Nodos que no requieren acción semántica directa o son manejados por otros ---
    def visit_Parameters(self, node: Parameters):
        # Los parámetros se manejan dentro de visit_FuncDecl
        pass
