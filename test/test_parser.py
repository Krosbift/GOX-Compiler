import unittest
from ..src.compiler.code_analyzer.parser import Parser
from lexer import Lexer
from ..src.compiler.ast_nodes import *

class TestParser(unittest.TestCase):
    def parse_code(self, code):
        lexer = Lexer(code)
        tokens = lexer.tokenize()
        parser = Parser(tokens)
        return parser.parse()

    def test_simple_assignment(self):
        program = self.parse_code("let x = 10;")
        self.assertIsInstance(program.statements[0], Assignment)
        self.assertEqual(program.statements[0].identifier, "x")

    def test_missing_semicolon(self):
        with self.assertRaises(SyntaxError):
            self.parse_code("let x = 10")

    def test_unexpected_token(self):
        with self.assertRaises(SyntaxError):
            self.parse_code("let x == 5;")

    def test_arithmetic_expression(self):
        program = self.parse_code("let x = 1 + 2 * 3;")
        assign = program.statements[0]
        self.assertIsInstance(assign.expression, BinaryOp)
        self.assertEqual(assign.expression.op, '+')

    def test_empty_program(self):
        program = self.parse_code("")
        self.assertEqual(len(program.statements), 0)

if __name__ == '__main__':
    unittest.main()
