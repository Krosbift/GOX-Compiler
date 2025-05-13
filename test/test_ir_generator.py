import unittest
from parser import Parser
from lexer import Lexer
from checker import SemanticChecker
from semantic_table import SemanticTable
from ir_generator import IRCodeGenerator

class TestIRCodeGenerator(unittest.TestCase):
    def generate_ir(self, code):
        lexer = Lexer(code)
        tokens = lexer.tokenize()
        parser = Parser(tokens)
        ast = parser.parse()
        checker = SemanticChecker(SemanticTable())
        checker.check(ast)
        generator = IRCodeGenerator()
        return generator.generate(ast)

    def test_assignment_ir(self):
        ir = self.generate_ir("let x = 5 + 3;")
        self.assertIn(('ADD', '5', '3', 't0'), ir)
        self.assertIn(('ASSIGN', 't0', 'x'), ir)

    def test_print_ir(self):
        ir = self.generate_ir("let x = 1; print(x);")
        self.assertIn(('PRINT', 'x'), ir)

    def test_chained_operations(self):
        ir = self.generate_ir("let x = 1 + 2 * 3;")
        self.assertTrue(any(instr[0] == 'MUL' for instr in ir))
        self.assertTrue(any(instr[0] == 'ADD' for instr in ir))

    def test_empty_code(self):
        ir = self.generate_ir("")
        self.assertEqual(ir, [])

if __name__ == '__main__':
    unittest.main()
