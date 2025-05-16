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
        self.semantic_symbol_table = semantic_symbol_table
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
            ("int", "float"): [("ITOF",)],
            ("float", "int"): [("FTOI",)],
        }

    def generate(self, ast_root_node: Program) -> IRModule:
        self._pre_scan_declarations(ast_root_node.statements)
        init_func_name = "main"
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
            user_main_ir_name = (
                "_actual_main" if user_main_sym.name == "main" else user_main_sym.name
            )
            self.current_function.append(("CALL", user_main_ir_name))
        else:
            self.current_function.append(("CONSTI", 0))
        self.current_function.append(("RET",))
        self.current_scope_path.pop()
        user_func_decls = [
            s for s in ast_root_node.statements if isinstance(s, FuncDecl)
        ]
        for func_decl_node in user_func_decls:
            self._visit(func_decl_node)
        self.current_function = None
        return self.module

    def _pre_scan_declarations(self, statements):
        for stmt in statements:
            if isinstance(stmt, VarDecl):
                var_name = stmt.identifier
                var_sym = self.semantic_symbol_table.global_scope.lookup(var_name)
                if var_sym and var_sym.type:
                    ir_type = _typemap.get(var_sym.type)
                    if ir_type and var_name not in self.module.globals:
                        self.module.globals[var_name] = IRGlobal(var_name, ir_type)
            elif isinstance(stmt, FuncDecl):
                func_name = stmt.identifier
                ir_func_name = "_actual_main" if func_name == "main" else func_name
                if ir_func_name not in self.module.functions:
                    parmnames = (
                        [p[0] for p in stmt.parameters.params]
                        if stmt.parameters
                        else []
                    )
                    func_sym_semantic = self.semantic_symbol_table.global_scope.lookup(
                        func_name
                    )
                    if not func_sym_semantic:
                        continue
                    parmtypes_lang = [
                        p_info["type"] for p_info in func_sym_semantic.params_info
                    ]
                    parmtypes_ir = [
                        _typemap.get(t, "I") for t in parmtypes_lang
                    ]
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
        for scope_semantic in reversed(self.current_scope_path):
            symbol = scope_semantic.lookup(name)
            if symbol:
                return symbol
        return None

    def _get_node_semantic_type(self, node: Expression) -> str | None:
        if hasattr(node, "semantic_type") and node.semantic_type is not None:
            return node.semantic_type
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
                self._emit(("CONSTI", ord(s)))
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
            self._emit(("CONSTI", 1))
        elif node.type_token == "FALSE":
            self._emit(("CONSTI", 0))

    def _visit_IdentifierLocation(self, node: IdentifierLocation):
        var_name = node.name
        sym_semantic = self._get_semantic_symbol(var_name)
        if not sym_semantic:
            return
        if self.current_function and var_name in self.current_function.locals:
            self._emit(("LOCAL_GET", var_name))
        elif var_name in self.module.globals:
            self._emit(("GLOBAL_GET", var_name))
        else:
            if self.current_function and self.current_function.name == "main":
                if var_name in self.module.globals:
                    self._emit(("GLOBAL_GET", var_name))
                else:
                    pass
            else:
                self._emit(("LOCAL_GET", var_name))

    def _visit_BinaryOp(self, node: BinaryOp):
        left_type_lang = self._get_node_semantic_type(node.left)
        op = node.op
        if op == "&&":
            if not (left_type_lang == "bool"):
                self._emit(("CONSTI", 0)) 
                return
            self._visit(node.left)
            self._emit(("IF",))
            right_type_lang = self._get_node_semantic_type(node.right)
            if not (right_type_lang == "bool"):
                self._emit(("CONSTI", 0))
            else:
                self._visit(node.right)
            self._emit(("ELSE",))
            self._emit(("CONSTI", 0))
            self._emit(("ENDIF",))
            return
        elif op == "||":
            if not (left_type_lang == "bool"):
                self._emit(("CONSTI", 0))
                return
            self._visit(node.left)
            self._emit(("IF",))
            self._emit(("CONSTI", 1))
            self._emit(("ELSE",))
            right_type_lang = self._get_node_semantic_type(node.right)
            if not (right_type_lang == "bool"):
                self._emit(("CONSTI", 0))
            else:
                self._visit(node.right)
            self._emit(("ENDIF",))
            return
        right_type_lang = self._get_node_semantic_type(node.right)
        if not left_type_lang or not right_type_lang:
            return
        if op == '/':
            self._visit(node.right)
            self._emit(("DUP",))
            is_float_division_check = (right_type_lang == "float")
            if is_float_division_check:
                self._emit(("CONSTF", 0.0))
                self._emit(("EQF",))
            else:
                self._emit(("CONSTI", 0))
                self._emit(("EQI",))
            self._emit(("IF",))
            self._emit(("POP", 1))
            self._emit(("RUNTIME_ERROR", "DivisionByZero"))
            self._emit(("ELSE",))
            self._visit(node.left)
            left_type_lang_effective = self._get_node_semantic_type(node.left)
            right_type_lang_effective = right_type_lang
            if not left_type_lang_effective or not right_type_lang_effective: return
            is_float_op_div = (left_type_lang_effective == "float" or right_type_lang_effective == "float")
            if is_float_op_div:
                if left_type_lang_effective == "int":
                    self._emit(("ITOF",))
                    left_type_lang_effective = "float"
                if right_type_lang_effective == "int":
                    right_type_lang_effective = "float"
            self._emit(("SWAP",))
            div_op_key_left = "float" if left_type_lang_effective == "float" else "int"
            div_op_key_right = "float" if right_type_lang_effective == "float" else "int"
            div_op_lookup_key = (div_op_key_left, '/', div_op_key_right)
            if div_op_lookup_key in self._binop_ircode:
                self._emit((self._binop_ircode[div_op_lookup_key],))
            else:
                self._emit(("CONSTI", 0))
            self._emit(("ENDIF",))
            return
        self._visit(node.left)
        left_type_lang_effective = self._get_node_semantic_type(node.left)
        self._visit(node.right)
        right_type_lang_effective = self._get_node_semantic_type(node.right)
        if not left_type_lang_effective or not right_type_lang_effective:
            return
        op_char = op
        is_float_op = False
        if op_char in ["+", "-", "*", "<", "<=", ">", ">=", "==", "!="]:
            if (
                left_type_lang_effective == "float"
                or right_type_lang_effective == "float"
            ):
                is_float_op = True
        if is_float_op:
            if right_type_lang_effective == "int":
                self._emit(("ITOF",)) 
                right_type_lang_effective = "float"
            if left_type_lang_effective == "int":
                left_type_lang_effective = "float"
        key_left = ("int" if left_type_lang_effective in ("char", "bool") else left_type_lang_effective)
        key_right = ("int" if right_type_lang_effective in ("char", "bool") else right_type_lang_effective)
        if is_float_op:  
            key_left = "float"
            key_right = "float"
        op_key = (key_left, op_char, key_right)
        if op_key in self._binop_ircode:
            self._emit((self._binop_ircode[op_key],))
        else:
            pass

    def _visit_UnaryOp(self, node: UnaryOp):
        self._visit(node.expr)
        expr_type_lang = self._get_node_semantic_type(node.expr)
        if not expr_type_lang:
            return
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
            pass

    def _visit_FuncDecl(self, node: FuncDecl):
        func_name_ast = node.identifier
        ir_func_name = "_actual_main" if func_name_ast == "main" else func_name_ast
        if ir_func_name not in self.module.functions:
            return
        target_ir_func = self.module.functions[ir_func_name]
        if node.is_import:
            target_ir_func.imported = True
            return
        previous_function = self.current_function
        self.current_function = target_ir_func
        func_sem_scope = None
        if hasattr(node, "semantic_scope") and node.semantic_scope:
            func_sem_scope = node.semantic_scope
        else:
            for child_scope in self.semantic_symbol_table.global_scope.children_scopes:
                if (
                    child_scope.scope_name == f"<func_body_{func_name_ast}>"
                ):
                    func_sem_scope = child_scope
                    break
        if not func_sem_scope:
            self.current_function = previous_function
            return
        self.current_scope_path.append(func_sem_scope)
        for pname, ptype_ir in zip(target_ir_func.parmnames, target_ir_func.parmtypes):
            target_ir_func.new_local(pname, ptype_ir)
        for stmt_node in node.body:
            self._visit(stmt_node)
        self.current_scope_path.pop()
        self.current_function = previous_function

    def _visit_FunctionCall(self, node: FunctionCall):
        if node.arguments:
            for arg_expr in node.arguments:
                self._visit(arg_expr)
        ir_call_name = "_actual_main" if node.name == "main" else node.name
        self._emit(("CALL", ir_call_name))

    def _visit_ReturnStmt(self, node: ReturnStmt):
        self._visit(node.expression)
        self._emit(("RET",))

    def _visit_PrintStmt(self, node: PrintStmt):
        self._visit(node.expression)
        expr_type_lang = self._get_node_semantic_type(node.expression)
        if not expr_type_lang:
            return
        if (
            expr_type_lang == "int" or expr_type_lang == "bool"
        ):
            self._emit(("PRINTI",))
        elif expr_type_lang == "float":
            self._emit(("PRINTF",))
        elif expr_type_lang == "char":
            self._emit(("PRINTB",))
        else:
            pass

    def _visit_IfStmt(self, node: IfStmt):
        self._visit(node.condition)
        self._emit(("IF",))
        for stmt in node.then_block:
            self._visit(stmt)
        if node.else_block:
            self._emit(("ELSE",))
            for stmt in node.else_block:
                self._visit(stmt)
        self._emit(("ENDIF",))

    def _visit_WhileStmt(self, node: WhileStmt):
        self._emit(("LOOP",))
        self._visit(
            node.condition
        )
        self._emit(("CONSTI", 1))
        self._emit(("SUBI",))
        self._emit(
            ("CBREAK",)
        )
        for stmt in node.body:
            self._visit(stmt)
        self._emit(("ENDLOOP",))

    def _visit_BreakStmt(self, node: BreakStmt):
        self._emit(("CONSTI", 1))
        self._emit(("CBREAK",))

    def _visit_ContinueStmt(self, node: ContinueStmt):
        self._emit(("CONTINUE",))

    def _visit_Cast(self, node: Cast):
        self._visit(node.expression)
        from_type_lang = self._get_node_semantic_type(node.expression)
        to_type_lang = node.cast_type
        if not from_type_lang:
            return
        if from_type_lang != to_type_lang:
            cast_key = (from_type_lang, to_type_lang)
            if cast_key in self._typecast_ircode:
                for instr_tuple in self._typecast_ircode[cast_key]:
                    self._emit(instr_tuple)

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
            self._emit(("PEEKI",))

    def _visit_Parameters(self, node: Parameters):
        pass

    def _visit_Type(self, node: Type):
        pass

    def _visit_Statement(self, node: Statement):
        pass

    def _visit_Expression(self, node: Expression):
        pass
