from typing import Type
from ..shared.AST.nodes.statement_node import Statement
from ..shared.AST.nodes.expression_node import Expression
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
from ..shared.symtable.symtable import SymbolTable as SemanticSymbolTable
from ..shared.symtable.symbol import SymbolKind as SemanticSymbolKind


class IRModule:
    def __init__(self):
        self.functions = {}
        self.globals = {}

    def dump(self):
        print("MODULE:::")
        for glob in self.globals.values():
            glob.dump()

        for func in self.functions.values():
            func.dump()


class IRGlobal:
    def __init__(self, name, type):
        self.name = name
        self.type = type

    def dump(self):
        print(f"GLOBAL::: {self.name}: {self.type}")


class IRFunction:
    def __init__(self, module, name, parmnames, parmtypes, return_type, imported=False):
        self.module = module
        module.functions[name] = self

        self.name = name
        self.parmnames = parmnames
        self.parmtypes = parmtypes
        self.return_type = return_type
        self.imported = imported
        self.locals = {}
        self.code = []

    def new_local(self, name, type):
        self.locals[name] = type

    def append(self, instr):
        self.code.append(instr)

    def extend(self, instructions):
        self.code.extend(instructions)

    def dump(self):
        print(
            f"FUNCTION::: {self.name}, {self.parmnames}, {self.parmtypes} {self.return_type}"
        )
        print(f"locals: {self.locals}")
        for instr in self.code:
            print(instr)


_typemap = {
    "int": "I",
    "float": "F",
    "bool": "I",
    "char": "I",
}


class IRCodeGenerator:
    def __init__(self, semantic_symbol_table: SemanticSymbolTable):
        self.semantic_symbol_table = (
            semantic_symbol_table  # Tabla de símbolos del Checker
        )
        self.module = IRModule()
        self.current_function: IRFunction | None = None
        self.current_scope_path = []
        self._binop_ircode = {
            ("int", "+", "int"): "ADDI",
            ("int", "-", "int"): "SUBI",
            ("int", "*", "int"): "MULI",
            ("int", "/", "int"): "DIVI",
            ("int", "<", "int"): "LTI",
            ("int", "<=", "int"): "LEI",
            ("int", ">", "int"): "GTI",
            ("int", ">=", "int"): "GEI",
            ("int", "==", "int"): "EQI",
            ("int", "!=", "int"): "NEI",
            ("float", "+", "float"): "ADDF",
            ("float", "-", "float"): "SUBF",
            ("float", "*", "float"): "MULF",
            ("float", "/", "float"): "DIVF",
            ("float", "<", "float"): "LTF",
            ("float", "<=", "float"): "LEF",
            ("float", ">", "float"): "GTF",
            ("float", ">=", "float"): "GEF",
            ("float", "==", "float"): "EQF",
            ("float", "!=", "float"): "NEF",
            ("char", "<", "char"): "LTI",
            ("char", "<=", "char"): "LEI",
            ("char", ">", "char"): "GTI",
            ("char", ">=", "char"): "GEI",
            ("char", "==", "char"): "EQI",
            ("char", "!=", "char"): "NEI",
        }
        self._unaryop_ircode = {
            ("+", "int"): [],
            ("+", "float"): [],
            ("-", "int"): [("CONSTI", -1), ("MULI",)],
            ("-", "float"): [("CONSTF", -1.0), ("MULF",)],
            ("!", "bool"): [("CONSTI", -1), ("MULI",)],
            ("^", "int"): [("GROW",)],
        }

        self._typecast_ircode = {
            # (from, to) : [ ops ]
            ("int", "float"): [("ITOF",)],
            ("float", "int"): [("FTOI",)],
        }

    def generate(self, ast_root_node: Program) -> IRModule:
        self._pre_scan_declarations(ast_root_node.statements)

        init_func_name = "main"  # Nombre de la función IR que envuelve todo
        if (
            "main" in self.module.functions
            and not self.module.functions["main"].imported
        ):
            pass

        self.current_function = IRFunction(
            self.module, init_func_name, [], [], _typemap["int"]
        )
        self.current_scope_path.append(self.semantic_symbol_table.global_scope)

        global_stmts = [
            s for s in ast_root_node.statements if not isinstance(s, FuncDecl)
        ]
        for stmt in global_stmts:
            self._visit(stmt)

        user_main_sym = self.semantic_symbol_table.global_scope.lookup("main")
        if user_main_sym and user_main_sym.kind == SemanticSymbolKind.FUNCTION:
            # Mapear el nombre si es necesario (tu ircode.py usa '_actual_main')
            user_main_ir_name = (
                "_actual_main" if user_main_sym.name == "main" else user_main_sym.name
            )
            self.current_function.append(("CALL", user_main_ir_name))
        else:
            # Si no hay main de usuario, _init simplemente retorna 0
            self.current_function.append(("CONSTI", 0))

        self.current_function.append(("RET",))
        self.current_scope_path.pop()  # Salir del global scope para _init

        # 5. Procesar cada FuncDecl para generar el código de sus cuerpos
        user_func_decls = [
            s for s in ast_root_node.statements if isinstance(s, FuncDecl)
        ]
        for func_decl_node in user_func_decls:
            self._visit(func_decl_node)  # Esto cambiará self.current_function

        self.current_function = None
        return self.module

    def _pre_scan_declarations(self, statements):
        # Registrar globales y firmas de funciones
        for stmt in statements:
            if isinstance(stmt, VarDecl):
                var_name = stmt.identifier
                var_sym = self.semantic_symbol_table.global_scope.lookup(var_name)
                if var_sym and var_sym.type:  # Si está en el scope global y tiene tipo
                    ir_type = _typemap.get(var_sym.type)
                    if ir_type and var_name not in self.module.globals:
                        self.module.globals[var_name] = IRGlobal(var_name, ir_type)

            elif isinstance(stmt, FuncDecl):
                func_name = stmt.identifier
                # Mapear 'main' a '_actual_main' para IR si es necesario
                ir_func_name = "_actual_main" if func_name == "main" else func_name

                if ir_func_name not in self.module.functions:
                    # Obtener información de parámetros y retorno del nodo AST
                    parmnames = (
                        [p[0] for p in stmt.parameters.params]
                        if stmt.parameters
                        else []
                    )
                    # Los tipos de parámetro y retorno deben venir del NODO AST o de la tabla semántica
                    # El checker debería haber validado los tipos.
                    # Necesitamos consultar la tabla semántica para los tipos reales.
                    func_sym_semantic = self.semantic_symbol_table.global_scope.lookup(
                        func_name
                    )
                    if not func_sym_semantic:
                        continue  # Error ya reportado por checker

                    parmtypes_lang = [
                        p_info["type"] for p_info in func_sym_semantic.params_info
                    ]
                    parmtypes_ir = [
                        _typemap.get(t, "I") for t in parmtypes_lang
                    ]  # Default a 'I' si no mapea

                    rettype_lang = func_sym_semantic.return_type
                    rettype_ir = _typemap.get(rettype_lang, "I")

                    IRFunction(
                        self.module,
                        ir_func_name,
                        parmnames,
                        parmtypes_ir,
                        rettype_ir,
                        stmt.is_import,
                    )

    def _get_semantic_symbol(self, name: str):
        """Busca un símbolo semántico subiendo por la pila de scopes actuales."""
        for scope_semantic in reversed(self.current_scope_path):
            symbol = scope_semantic.lookup(name)
            if symbol:
                return symbol
        return None

    def _get_node_semantic_type(self, node: Expression) -> str | None:
        """
        Obtiene el tipo semántico de un nodo de expresión.
        Esto es un placeholder. Idealmente, el Checker anota los nodos AST con su tipo
        o tenemos una forma de consultarlo robustamente.
        """
        if hasattr(node, "semantic_type") and node.semantic_type is not None:
            return node.semantic_type

        # Fallback muy simple (NO ROBUSTO):
        if isinstance(node, Literal):
            if node.type_token == "INTEGER":
                return "int"
            if node.type_token == "FLOAT":
                return "float"
            if node.type_token == "CHAR":
                return "char"
            if node.type_token in ("TRUE", "FALSE"):
                return "bool"
        elif isinstance(node, IdentifierLocation):
            sym = self._get_semantic_symbol(node.name)
            return sym.type if sym else None
        return None

    def _emit(self, instruction):
        if self.current_function:
            self.current_function.append(instruction)
        else:
            raise Exception(
                "IR Generation Error: No current function to emit code into."
            )

    def _visit(self, node):
        if node is None:
            return
        method_name = f"_visit_{node.__class__.__name__}"
        visitor = getattr(self, method_name, self._generic_visit)
        return visitor(node)

    def _generic_visit(self, node):
        raise NotImplementedError(f"No IR generator visitor for {type(node)}")

    def _visit_Program(self, node: Program):
        pass

    def _visit_VarDecl(self, node: VarDecl):
        var_name = node.identifier
        is_global_context = (
            self.current_function is not None
            and self.current_function.name == "main"
            and self.current_function.module.functions[self.current_function.name]
            == self.current_function
        )

        var_sym_semantic = self._get_semantic_symbol(var_name)
        if not var_sym_semantic or not var_sym_semantic.type:
            return

        var_ir_type = _typemap.get(var_sym_semantic.type)
        if not var_ir_type:
            return

        if is_global_context:
            if node.initializer:
                self._visit(node.initializer)
                self._emit(("GLOBAL_SET", var_name))
        else:
            if var_name not in self.current_function.locals:
                self.current_function.new_local(var_name, var_ir_type)
            if node.initializer:
                self._visit(node.initializer)
                self._emit(("LOCAL_SET", var_name))

    def _visit_Assignment(self, node: Assignment):
        location_node = node.location
        if isinstance(location_node, IdentifierLocation):
            self._visit(node.expression)
            var_name = location_node.name
            sym_semantic = self._get_semantic_symbol(var_name)
            if not sym_semantic:
                return
            if self.current_function and var_name in self.current_function.locals:
                self._emit(("LOCAL_SET", var_name))
            elif var_name in self.module.globals:
                self._emit(("GLOBAL_SET", var_name))
            else:
                if self.current_function and self.current_function.name == "main":
                    if var_name in self.module.globals:
                        self._emit(("GLOBAL_SET", var_name))
                    else:
                        pass
                else:
                    self._emit(("LOCAL_SET", var_name))

        elif isinstance(location_node, DereferenceLocation):
            self._visit(location_node.expression)
            self._visit(node.expression)
            value_type_lang = self._get_node_semantic_type(node.expression)
            if value_type_lang == "int" or value_type_lang == "bool":
                self._emit(("POKEI",))
            elif value_type_lang == "float":
                self._emit(("POKEF",))
            elif value_type_lang == "char":
                self._emit(("POKEB",))
            else:
                raise NotImplementedError(
                    f"IR no implementado para asignación a {type(location_node)}"
                )
        else:
            raise NotImplementedError(
                f"IR no implementado para asignación a {type(location_node)}"
            )

    def _visit_Literal(self, node: Literal):
        # AST Literal(value, type_token)
        # type_token: 'INTEGER', 'FLOAT', 'CHAR', 'TRUE', 'FALSE'
        if node.type_token == "INTEGER":
            self._emit(("CONSTI", int(node.value)))
        elif node.type_token == "FLOAT":
            self._emit(("CONSTF", float(node.value)))
        elif node.type_token == "CHAR":
            s = (
                node.value[1:-1]
                if len(node.value) >= 2
                and node.value.startswith("'")
                and node.value.endswith("'")
                else node.value
            )

            if isinstance(s, str) and len(s) == 1:
                self._emit(("CONSTI", ord(s)))  # Chars son ints
            else:
                processed_char = s
                if s == "\\n":
                    processed_char = "\n"
                elif s == "\\t":
                    processed_char = "\t"
                elif s == "\\r":
                    processed_char = "\r"
                elif s == "\\'":
                    processed_char = "'"
                elif s == '\\"':
                    processed_char = '"'
                elif s == "\\\\":
                    processed_char = "\\"

                if len(processed_char) == 1:
                    self._emit(("CONSTI", ord(processed_char)))
                else:
                    self._emit(("CONSTI", ord("?")))
                    self._add_error(
                        f"Valor de literal CHAR inválido encontrado: {repr(s)}. Esperaba un solo carácter.",
                        node,
                    )
        elif node.type_token == "TRUE":
            self._emit(("CONSTI", 1))  # Bools son ints
        elif node.type_token == "FALSE":
            self._emit(("CONSTI", 0))

    def _visit_IdentifierLocation(self, node: IdentifierLocation):
        # Esto es para cuando un ID se usa como VALOR (lado derecho o en expresión)
        var_name = node.name
        sym_semantic = self._get_semantic_symbol(var_name)
        if not sym_semantic:
            return  # Error

        if self.current_function and var_name in self.current_function.locals:
            self._emit(("LOCAL_GET", var_name))
        elif var_name in self.module.globals:
            self._emit(("GLOBAL_GET", var_name))
        else:  # Similar a Assignment, manejo de scopes
            if self.current_function and self.current_function.name == "main":  # _init
                if var_name in self.module.globals:
                    self._emit(("GLOBAL_GET", var_name))
                else:
                    # print(f"Error IR: GET de '{var_name}' no es local ni global conocido en _init.")
                    pass
            else:  # En función de usuario, debe ser local o param
                self._emit(("LOCAL_GET", var_name))

    def _visit_BinaryOp(self, node: BinaryOp):
        # Necesitamos los tipos de los operandos para elegir ADDI/ADDF etc.
        # El Checker debería haberlos determinado. Asumimos que podemos obtenerlos.
        # Si el Checker anota los nodos con .semantic_type:
        left_type_lang = self._get_node_semantic_type(node.left)
        right_type_lang = self._get_node_semantic_type(node.right)
        op = node.op

        if not left_type_lang or not right_type_lang:
            # print(f"Error IR: No se pudieron determinar tipos para BinaryOp {op}")
            return

        # Manejo especial para && y || (cortocircuito)
        # Tu IR no tiene saltos. IF/ELSE/ENDIF son marcadores.
        # Simular &&:  left IF right ELSE CONSTI 0 ENDIF
        # Simular ||:  left IF CONSTI 1 ELSE right ENDIF
        if op == "&&":
            self._visit(node.left)  # Evalúa left, deja bool (I) en pila
            self._emit(("IF",))  # Si left es true (1)...
            self._visit(node.right)  #   Evalúa right, deja bool (I) en pila
            self._emit(("ELSE",))  # Si left es false (0)...
            self._emit(("CONSTI", 0))  #   Apila false (0)
            self._emit(("ENDIF",))  # Fin. Pila tiene resultado de &&
            return
        elif op == "||":
            self._visit(node.left)  # Evalúa left, deja bool (I) en pila
            self._emit(("IF",))  # Si left es true (1)...
            self._emit(("CONSTI", 1))  #   Apila true (1)
            self._emit(("ELSE",))  # Si left es false (0)...
            self._visit(node.right)  #   Evalúa right, deja bool (I) en pila
            self._emit(("ENDIF",))  # Fin. Pila tiene resultado de ||
            return

        self._visit(node.left)  # Pila: [L]
        left_type_lang_effective = self._get_node_semantic_type(
            node.left
        )  # Tipo real de L

        self._visit(node.right)  # Pila: [L, R]
        right_type_lang_effective = self._get_node_semantic_type(
            node.right
        )  # Tipo real de R

        if not left_type_lang_effective or not right_type_lang_effective:
            return

        # Determinar el tipo de operación (int o float)
        # (char/bool se tratan como int para la operación)
        op_char = node.op
        is_float_op = False
        if op_char in ["+", "-", "*", "/", "<", "<=", ">", ">=", "==", "!="]:
            if (
                left_type_lang_effective == "float"
                or right_type_lang_effective == "float"
            ):
                is_float_op = True

        # Coerción: si la operación es float y un operando es int, convertirlo
        # Pila actual: [L, R_tope]
        if is_float_op:
            if right_type_lang_effective == "int":
                self._emit(("ITOF",))  # Convierte R (tope) a float
                right_type_lang_effective = "float"
            # Ahora L está debajo, R (como float) está arriba.
            # Si L necesita conversión:
            if left_type_lang_effective == "int":
                self._emit(("SWAP",))  # Pila: [R(F), L(I)_tope]
                self._emit(("ITOF",))  # Pila: [R(F), L(F)_tope]
                self._emit(
                    ("SWAP",)
                )  # Pila: [L(F), R(F)_tope] (orden original para la operación)

        # Tipos para buscar el opcode IR
        key_left = (
            "int"
            if left_type_lang_effective in ("char", "bool")
            else left_type_lang_effective
        )
        key_right = (
            "int"
            if right_type_lang_effective in ("char", "bool")
            else right_type_lang_effective
        )
        if is_float_op:  # Si la operación fue float, ambos keys deben ser float
            key_left = "float"
            key_right = "float"

        op_key = (key_left, op_char, key_right)
        if op_key in self._binop_ircode:
            self._emit((self._binop_ircode[op_key],))
        else:
            # print(f"Error IR: Operador binario no soportado para tipos {op_key}")
            pass

    def _visit_UnaryOp(self, node: UnaryOp):
        self._visit(node.expr)  # Deja valor de expr en la pila

        expr_type_lang = self._get_node_semantic_type(node.expr)
        if not expr_type_lang:
            return

        # El tipo para la clave del operador
        key_expr_type = (
            "bool"
            if expr_type_lang == "bool"
            else "int" if expr_type_lang == "char" else expr_type_lang
        )

        op_key = (node.op, key_expr_type)
        if op_key in self._unaryop_ircode:
            for instr_tuple in self._unaryop_ircode[op_key]:
                self._emit(instr_tuple)
        else:
            # print(f"Error IR: Operador unario no soportado {op_key}")
            pass

    def _visit_FuncDecl(self, node: FuncDecl):
        func_name_ast = node.identifier
        ir_func_name = "_actual_main" if func_name_ast == "main" else func_name_ast

        # La función ya debe existir en self.module.functions por _pre_scan_declarations
        if ir_func_name not in self.module.functions:
            # print(f"Error IR: Definición de función '{ir_func_name}' no encontrada en pre-scan.")
            # Podríamos crearla aquí como fallback si el pre-scan falló o no se hizo.
            # Pero es mejor que el pre-scan la haya creado.
            return

        target_ir_func = self.module.functions[ir_func_name]

        if node.is_import:  # Nada que generar para importadas
            target_ir_func.imported = True
            return

        # Guardar función actual (podría ser _init), y cambiar a esta.
        previous_function = self.current_function
        self.current_function = target_ir_func

        # Entrar al scope semántico de la función
        # Necesitamos encontrar el scope semántico correspondiente a esta función
        # Esto es un poco más complejo que solo el nombre, podría haber funciones anidadas (no en tu gramática)
        # o sobrecargas (tampoco). Por ahora, lookup por nombre en global.
        func_sem_scope = None
        # El checker crea un scope para la función. Necesitamos una forma de acceder a él.
        # Si los nodos AST son anotados con su scope semántico por el checker:
        if hasattr(node, "semantic_scope") and node.semantic_scope:
            func_sem_scope = node.semantic_scope
        else:  # Fallback buscando en los hijos del global (no ideal)
            for child_scope in self.semantic_symbol_table.global_scope.children_scopes:
                if (
                    child_scope.scope_name == f"<func_body_{func_name_ast}>"
                ):  # Nombre del scope del checker
                    func_sem_scope = child_scope
                    break

        if not func_sem_scope:
            # print(f"Error IR: No se encontró el scope semántico para la función {func_name_ast}")
            self.current_function = previous_function  # Restaurar
            return

        self.current_scope_path.append(func_sem_scope)

        # Registrar locales (parámetros ya están en IRFunction por pre-scan, pero aquí los declaramos como locales)
        # Los parámetros son los primeros locales.
        for pname, ptype_ir in zip(target_ir_func.parmnames, target_ir_func.parmtypes):
            target_ir_func.new_local(pname, ptype_ir)
        for stmt_node in node.body:
            self._visit(stmt_node)
        self.current_scope_path.pop()  # Salir del scope de la función
        self.current_function = previous_function  # Restaurar función IR anterior

    def _visit_FunctionCall(self, node: FunctionCall):
        # 1. Evaluar argumentos y ponerlos en la pila (en orden inverso de declaración o según convención)
        #    La convención de C es usualmente argumentos de derecha a izquierda.
        #    Si los parámetros son (a, b, c), y la llamada es f(x,y,z),
        #    se apila z, luego y, luego x.
        #    Asumamos orden de izquierda a derecha para la evaluación en la pila por ahora.
        if node.arguments:
            for arg_expr in node.arguments:
                self._visit(arg_expr)

        # Mapear 'main' a '_actual_main' si es necesario
        ir_call_name = "_actual_main" if node.name == "main" else node.name
        self._emit(("CALL", ir_call_name))

    def _visit_ReturnStmt(self, node: ReturnStmt):
        self._visit(node.expression)  # Deja el valor de retorno en la pila
        self._emit(("RET",))

    def _visit_PrintStmt(self, node: PrintStmt):
        self._visit(node.expression)  # Deja valor en la pila

        # Determinar tipo para PRINTI/F/B
        expr_type_lang = self._get_node_semantic_type(node.expression)
        if not expr_type_lang:
            return

        if (
            expr_type_lang == "int" or expr_type_lang == "bool"
        ):  # Bool se imprime como int
            self._emit(("PRINTI",))
        elif expr_type_lang == "float":
            self._emit(("PRINTF",))
        elif expr_type_lang == "char":
            self._emit(("PRINTB",))  # PRINTB imprime el char correspondiente al int
        else:
            # print(f"Error IR: Tipo no soportado para PRINT: {expr_type_lang}")
            pass

    def _visit_IfStmt(self, node: IfStmt):
        self._visit(node.condition)  # Deja bool (I) en la pila
        self._emit(("IF",))

        # Entrar a un nuevo scope semántico para el 'then' block si el checker los crea
        # self.current_scope_path.append(node.then_block_scope_semantic)
        for stmt in node.then_block:
            self._visit(stmt)
        # self.current_scope_path.pop()

        if node.else_block:
            self._emit(("ELSE",))
            # self.current_scope_path.append(node.else_block_scope_semantic)
            for stmt in node.else_block:
                self._visit(stmt)
            # self.current_scope_path.pop()

        self._emit(("ENDIF",))

    def _visit_WhileStmt(self, node: WhileStmt):
        self._emit(("LOOP",))
        # La condición se evalúa DENTRO del loop en tu ircode.py:
        # LOOP
        # CONSTI 1
        # <evaluar test> (deja 0 si test es true para seguir, 1 si test es false para romper)
        # SUBI
        # CBREAK
        # ...body...
        # ENDLOOP
        # Esto es: CBREAK si (1 - test_original_como_bool) es true, o sea si test_original es false.
        # Si test_original es true (1), 1 - 1 = 0. CBREAK no salta.
        # Si test_original es false (0), 1 - 0 = 1. CBREAK salta.

        # Código para evaluar la condición negada para CBREAK
        self._visit(
            node.condition
        )  # Deja el bool de la condición (1 para true, 0 para false)
        # Queremos CBREAK si la condición es FALSA.
        # CBREAK salta si el tope de la pila es distinto de cero.
        # Si condición es true (1), necesitamos 0 en la pila para NO saltar.
        # Si condición es false (0), necesitamos 1 en la pila para SÍ saltar.
        # Esto es equivalente a NOT condición.
        # (NOT X) es (CONSTI 1, SWAP, SUBI)
        self._emit(("CONSTI", 1))
        self._emit(("SWAP",))  # Pila: [1, cond_val]
        self._emit(("SUBI",))  # Pila: [1 - cond_val] -> esto es (NOT cond_val)

        self._emit(
            ("CBREAK",)
        )  # Rompe si (NOT cond_val) es true (o sea, si cond_val es false)

        # Cuerpo del bucle
        # self.current_scope_path.append(node.body_scope_semantic)
        for stmt in node.body:
            self._visit(stmt)
        # self.current_scope_path.pop()

        self._emit(("ENDLOOP",))

    def _visit_BreakStmt(self, node: BreakStmt):
        # CBREAK siempre necesita un valor en la pila. Rompe si no es cero.
        self._emit(("CONSTI", 1))  # Poner un valor no-cero para forzar la ruptura
        self._emit(("CBREAK",))

    def _visit_ContinueStmt(self, node: ContinueStmt):
        self._emit(("CONTINUE",))  # Vuelve al inicio del LOOP más cercano

    def _visit_Cast(self, node: Cast):
        self._visit(node.expression)  # Deja valor original en la pila

        from_type_lang = self._get_node_semantic_type(node.expression)
        to_type_lang = node.cast_type  # Este es el tipo de lenguaje del AST

        if not from_type_lang:
            return

        # Solo emitir instrucción de cast si es necesario según IR
        if from_type_lang != to_type_lang:
            cast_key = (from_type_lang, to_type_lang)
            if cast_key in self._typecast_ircode:
                for instr_tuple in self._typecast_ircode[cast_key]:
                    self._emit(instr_tuple)
            # Si no está en _typecast_ircode, significa que el cambio de tipo es solo semántico
            # y no requiere una instrucción IR (ej. int a bool, o char a int).

    def _visit_DereferenceLocation(self, node: DereferenceLocation):
        self._visit(node.expression)
        expected_type_lang = self._get_node_semantic_type(node)

        if expected_type_lang == "int" or expected_type_lang == "bool":
            self._emit(("PEEKI",))
        elif expected_type_lang == "float":
            self._emit(("PEEKF",))
        elif expected_type_lang == "char":
            self._emit(("PEEKB",))
        else:
            # print(f"Advertencia IR: No se pudo determinar el tipo para PEEK en DereferenceLocation. Asumiendo PEEKI.")
            self._emit(("PEEKI",))  # Fallback peligroso

    # Nodos que no generan código directamente o son manejados por sus padres
    def _visit_Parameters(self, node: Parameters):
        pass

    def _visit_Type(self, node: Type):
        pass

    # Statement y Expression son clases base abstractas
    def _visit_Statement(self, node: Statement):
        pass

    def _visit_Expression(self, node: Expression):
        pass
