from .lexical_analyzer.lexer import Lexer


class Compiler:
    def __init__(self, path_file: str):
        self.path_file = path_file
        self.get_tokens()

    def get_tokens(self):
        lexer = Lexer(self.path_file)
        tokens = lexer.analyze()
