from .lexical_analysis.lexical_analysis import LexicalAnalysis

class Compiler:
    def __init__(self, path_file):
        self.path_file = path_file
        self.tokens = self.get_tokens()

    def get_tokens(self):
        lexxer = LexicalAnalysis()
