import os
from .lexical_analyzer.lexer import Lexer
from .syntactical_analyzer.parser import Parser
from ..shared.json.ast_to_json import ASTtoJSON


class Compiler:
    def __init__(self, path_file):
        self.path_file = path_file
        self.compile()

    def compile(self):
        self.set_lexer()
        if (self.tokens == 0):
            return 0

        self.set_parser()
        self.gen_ast_to_json()

    def set_lexer(self):
        lexer = Lexer(self.path_file)
        self.tokens = lexer.analyze()

    def set_parser(self):
        parser = Parser(self.tokens)
        self.ast = parser.parse()

    def get_filename(self):
        return os.path.basename(self.path_file)

    def gen_ast_to_json(self):
        ASTtoJSON.convert_to_json(self.ast, self.get_filename())
