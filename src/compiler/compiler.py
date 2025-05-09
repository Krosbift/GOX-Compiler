from .code_analyzer.lexer import Lexer
from .code_analyzer.parser import Parser
from ..shared.json.ast_to_json import ASTtoJSON


class Compiler:
    def __init__(self, path_file):
        self.path_file = path_file
        self.compile()

    def compile(self):
        if self.code_verify() == 0:
            return 0

    def code_verify(self):
        return self.set_lexer() or self.set_parser()

    def set_lexer(self):
        self.tokens = Lexer(self.path_file).analyze()
        return False if self.tokens else True

    def set_parser(self):
        self.ast = Parser(self.tokens).parse()
        return False if self.ast else True
