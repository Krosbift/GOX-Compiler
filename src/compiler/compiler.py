from .code_analyzer.lexical_analyzer.lexer import Lexer
from .code_analyzer.syntactical_analyzer.parser import Parser


class Compiler:
    def __init__(self, path_file):
        self.path_file = path_file
        self.compile()

    def compile(self):
        self.set_lexer()
        if len(self.tokens) == 0:
            return 0

        self.set_parser()
        if self.ast == None:
            return 0

    def set_lexer(self):
        lexer = Lexer(self.path_file)
        self.tokens = lexer.analyze()

    def set_parser(self):
        parser = Parser(self.tokens)
        self.ast = parser.parse()
