from .lexical_analyzer.lexer import Lexer
from .syntactical_analyzer.parser import Parser
from ..shared.json.ast_to_json import ASTtoJSON

class Compiler:
    def __init__(self, path_file):
        self.path_file = path_file
        self.get_tokens()
        self.get_ast()

    def get_tokens(self):
        lexer = Lexer(self.path_file)
        self.tokens = lexer.analyze()

    def get_ast(self):
        parser = Parser(self.tokens)
        self.ast = parser.parse()
        ASTtoJSON.convert_to_json(self.ast)
