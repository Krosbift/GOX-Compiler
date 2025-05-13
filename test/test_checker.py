import unittest
from unittest.mock import Mock
import sys
import os

# Ajustar el PYTHONPATH para incluir el directorio raíz del proyecto
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.compiler.code_analyzer.checker import Checker
from src.compiler.shared.AST.grammar.vardecl import VarDecl
from src.compiler.shared.AST.grammar.assigment import Assignment
from src.compiler.shared.AST.grammar.identifier_location import IdentifierLocation
from src.compiler.shared.AST.grammar.literal import Literal
from src.compiler.shared.AST.grammar.binary_operator import BinaryOp
from src.compiler.shared.AST.grammar.funcdecl import FuncDecl
from src.compiler.shared.AST.grammar.if_stmt import IfStmt
from src.compiler.shared.AST.grammar.return_stmt import ReturnStmt
from src.compiler.shared.AST.grammar.parameters import Parameters
from src.compiler.shared.symtable.symbol import Symbol, SymbolKind
from src.compiler.shared.symtable.symtable import SymbolTable

def create_token(type, value, line=1, column=1):
    token = Mock()
    token.type = type
    token.value = value
    token.line = line
    token.column = column
    return token

class TestChecker(unittest.TestCase):
    def setUp(self):
        self.ast = Mock()
        self.checker = Checker(self.ast)
        self.checker.symbol_table = SymbolTable()
        self.checker.symbol_table.valid_types = {"int", "float", "char", "bool", "void"}

    # Tests para _visit_VarDecl
    def test_vardecl_valid(self):
        node = VarDecl(
            kind="var",
            identifier="x",
            var_type="int",
            initializer=Literal(value="42", type_token="INTEGER")
        )
        self.checker._visit_VarDecl(node)
        self.assertEqual(node.semantic_type, "int")
        self.assertIsNotNone(node.defined_symbol)
        self.assertEqual(node.defined_symbol.name, "x")
        self.assertEqual(node.defined_symbol.type, "int")
        self.assertEqual(node.defined_symbol.kind, SymbolKind.VARIABLE)
        self.assertEqual(len(self.checker.errors), 0)

    def test_vardecl_invalid_type(self):
        node = VarDecl(
            kind="var",
            identifier="x",
            var_type="invalid",
            initializer=None
        )
        self.checker._visit_VarDecl(node)
        self.assertIsNone(node.semantic_type)
        self.assertIsNone(node.defined_symbol)
        self.assertGreaterEqual(len(self.checker.errors), 1)
        self.assertIn("Tipo inválido 'invalid'", self.checker.errors[0])

    def test_vardecl_type_mismatch(self):
        node = VarDecl(
            kind="var",
            identifier="x",
            var_type="int",
            initializer=Literal(value="3.14", type_token="FLOAT")
        )
        self.checker._visit_VarDecl(node)
        self.assertEqual(node.semantic_type, "int")
        self.assertIsNotNone(node.defined_symbol)
        self.assertEqual(len(self.checker.errors), 1)
        self.assertIn("No se puede inicializar variable 'x' (tipo 'int') con un valor de tipo 'float'", self.checker.errors[0])

    # Tests para _visit_Assignment
    def test_assignment_valid(self):
        node = Assignment(
            location=IdentifierLocation(name="x"),
            expression=Literal(value="42", type_token="INTEGER")
        )
        self.checker.symbol_table.current_scope.define(
            Symbol(name="x", kind=SymbolKind.VARIABLE, sym_type="int")
        )
        self.checker._visit_Assignment(node)
        self.assertEqual(node.location.semantic_type, "int")
        self.assertEqual(node.expression.semantic_type, "int")
        self.assertEqual(len(self.checker.errors), 0)

    def test_assignment_undeclared(self):
        node = Assignment(
            location=IdentifierLocation(name="x"),
            expression=Literal(value="42", type_token="INTEGER")
        )
        self.checker._visit_Assignment(node)
        self.assertEqual(len(self.checker.errors), 1)
        self.assertIn("Asignación a variable no declarada 'x'", self.checker.errors[0])

    def test_assignment_to_constant(self):
        node = Assignment(
            location=IdentifierLocation(name="x"),
            expression=Literal(value="42", type_token="INTEGER")
        )
        self.checker.symbol_table.current_scope.define(
            Symbol(name="x", kind=SymbolKind.CONSTANT, sym_type="int")
        )
        self.checker._visit_Assignment(node)
        self.assertEqual(len(self.checker.errors), 1)
        self.assertIn("No se puede asignar a la constante 'x'", self.checker.errors[0])

    # Tests para _visit_BinaryOp
    def test_binaryop_valid(self):
        node = BinaryOp(
            left=Literal(value="1", type_token="INTEGER"),
            op="+",
            right=Literal(value="2", type_token="INTEGER")
        )
        self.checker._visit_BinaryOp(node)
        self.assertEqual(node.semantic_type, "int")
        self.assertEqual(len(self.checker.errors), 0)

    def test_binaryop_invalid_types(self):
        node = BinaryOp(
            left=Literal(value="'a'", type_token="CHAR"),
            right=Literal(value="true", type_token="TRUE"),
            op="+"
        )
        self.checker._visit_BinaryOp(node)
        self.assertIsNone(node.semantic_type)
        self.assertEqual(len(self.checker.errors), 1)
        self.assertIn("Operador binario '+' no se puede aplicar a operandos de tipo 'char' y 'bool'", self.checker.errors[0])

    # Tests para _visit_FuncDecl
    def test_funcdecl_valid(self):
        node = FuncDecl(
            is_import=False,
            identifier="f",
            parameters=Parameters(params=[("x", "int")]),
            return_type="int",
            body=[]
        )
        self.checker._visit_FuncDecl(node)
        self.assertIsNotNone(node.defined_symbol)
        self.assertEqual(node.defined_symbol.name, "f")
        self.assertEqual(node.defined_symbol.kind, SymbolKind.FUNCTION)
        self.assertEqual(node.defined_symbol.return_type, "int")
        self.assertEqual(len(node.defined_symbol.params_info), 1)
        self.assertEqual(len(self.checker.errors), 0)

    def test_funcdecl_invalid_return_type(self):
        node = FuncDecl(
            is_import=False,
            identifier="f",
            parameters=Parameters(params=[]),
            return_type="invalid",
            body=[]
        )
        self.checker._visit_FuncDecl(node)
        self.assertIsNotNone(node.defined_symbol)
        self.assertIsNone(node.defined_symbol.return_type)
        self.assertGreaterEqual(len(self.checker.errors), 1)
        self.assertIn("Tipo inválido 'invalid'", self.checker.errors[0])

    # Tests para _visit_IfStmt
    def test_ifstmt_valid(self):
        node = IfStmt(
            condition=Literal(value="true", type_token="TRUE"),
            then_block=[],
            else_block=None
        )
        self.checker._visit_IfStmt(node)
        self.assertEqual(node.condition.semantic_type, "bool")
        self.assertEqual(len(self.checker.errors), 0)

    def test_ifstmt_non_bool_condition(self):
        node = IfStmt(
            condition=Literal(value="1", type_token="INTEGER"),
            then_block=[],
            else_block=None
        )
        self.checker._visit_IfStmt(node)
        self.assertEqual(len(self.checker.errors), 1)
        self.assertIn("La condición de 'if' debe ser 'bool', pero es 'int'", self.checker.errors[0])

    # Tests para _visit_ReturnStmt
    def test_returnstmt_valid(self):
        node = ReturnStmt(
            expression=Literal(value="42", type_token="INTEGER")
        )
        func_symbol = Symbol(
            name="f",
            kind=SymbolKind.FUNCTION,
            sym_type=None,
            return_type="int",
            params_info=[]
        )
        self.checker.symbol_table.enter_scope("<func_body_f>", current_function_symbol=func_symbol)
        self.checker._visit_ReturnStmt(node)
        self.assertEqual(len(self.checker.errors), 0)

    def test_returnstmt_type_mismatch(self):
        node = ReturnStmt(
            expression=Literal(value="3.14", type_token="FLOAT")
        )
        func_symbol = Symbol(
            name="f",
            kind=SymbolKind.FUNCTION,
            sym_type=None,
            return_type="int",
            params_info=[]
        )
        self.checker.symbol_table.enter_scope("<func_body_f>", current_function_symbol=func_symbol)
        self.checker._visit_ReturnStmt(node)
        self.assertEqual(len(self.checker.errors), 1)
        self.assertIn("No se puede retornar un valor de tipo 'float' en una función que espera 'int'", self.checker.errors[0])

if __name__ == '__main__':
    unittest.main()