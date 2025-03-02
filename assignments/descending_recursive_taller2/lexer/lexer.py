import re
from .grammar.grammar import TOKEN_REGEX


class Lexer:
    def __init__(self, code):
        self.tokens = self.tokenize(code)
        self.pos = 0

    def tokenize(self, code):
        pattern = "|".join(
            f"(?P<{name}>{regex})" for name, regex in TOKEN_REGEX.items()
        )
        tokens = []
        for match in re.finditer(pattern, code):
            for name, value in match.groupdict().items():
                if value is not None:
                    tokens.append((name, value))
        return tokens

    def next_token(self):
        if self.pos < len(self.tokens):
            token = self.tokens[self.pos]
            self.pos += 1
            return token
        return ("EOF", "")

    def peek(self):
        if self.pos < len(self.tokens):
            return self.tokens[self.pos]
        return ("EOF", "")
