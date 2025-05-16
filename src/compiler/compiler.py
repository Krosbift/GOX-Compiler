from .code_analyzer.lexer import Lexer
from .code_analyzer.parser import Parser
from .code_analyzer.checker import Checker
from .interpreter.ir_generator import IRCodeGenerator


class Compiler:
    def __init__(self, path_file):
        self.path_file = path_file
        self.compile()

    def compile(self):
        if self.code_verify():
            return 0
        if self.gen_ircode():
            return 0
        print("\n--- MÓDULO IR GENERADO ---")
        self.ircode.dump()

    def code_verify(self):
        return self.set_lexer() or self.set_parser() or self.set_checker()

    def set_lexer(self):
        self.tokens = Lexer(self.path_file).analyze()
        return False if self.tokens else True

    def set_parser(self):
        self.ast = Parser(self.tokens).analyze()
        return False if self.ast else True

    def set_checker(self):
        self.symtable = Checker(self.ast).analyze()
        return False if self.symtable else True

    def gen_ircode(self):
        self.ircode = IRCodeGenerator(self.symtable).generate(self.ast)
        return False if self.ircode else True
