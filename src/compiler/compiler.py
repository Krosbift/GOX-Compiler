from .code_analyzer.lexer import Lexer
from .code_analyzer.parser import Parser
from .code_analyzer.senser import Senser


class Compiler:
    def __init__(self, path_file):
        self.path_file = path_file
        self.compile()

    def compile(self):
        if self.code_verify() == 0:
            return 0

    def code_verify(self):
        self.set_lexer()
        if len(self.tokens) <= 0:
            return 0

        self.set_parser()
        if self.ast == None:
            return 0

        self.set_senser()
        if self.sym_table == None:
            return 0

        return 1

    def set_lexer(self):
        lexer = Lexer(self.path_file)
        self.tokens = lexer.analyze()

    def set_parser(self):
        parser = Parser(self.tokens)
        self.ast = parser.parse()

    def set_senser(self):
        senser = Senser()
        self.sym_table = senser.analyze(self.ast)
