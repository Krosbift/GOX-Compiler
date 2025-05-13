import unittest
from ..compiler.code_analyzer.lexer import Lexer, Token, TokenType

class TestLexer(unittest.TestCase):
    def test_valid_tokens(self):
        lexer = Lexer("let x = 5 + 3;")
        tokens = lexer.tokenize()
        types = [token.type for token in tokens]
        self.assertEqual(types, [
            TokenType.LET, TokenType.IDENTIFIER, TokenType.ASSIGN,
            TokenType.NUMBER, TokenType.PLUS, TokenType.NUMBER,
            TokenType.SEMICOLON, TokenType.EOF
        ])

    def test_invalid_character(self):
        lexer = Lexer("let x = 5 $ 2;")
        with self.assertRaises(SyntaxError) as context:
            lexer.tokenize()
        self.assertIn("Illegal character", str(context.exception))

    def test_identifiers_and_keywords(self):
        lexer = Lexer("let print = 10;")
        tokens = lexer.tokenize()
        self.assertEqual(tokens[0].type, TokenType.LET)
        self.assertEqual(tokens[1].type, TokenType.IDENTIFIER)
        self.assertEqual(tokens[1].value, "print")

    def test_empty_input(self):
        lexer = Lexer("")
        tokens = lexer.tokenize()
        self.assertEqual(len(tokens), 1)
        self.assertEqual(tokens[0].type, TokenType.EOF)

if __name__ == '__main__':
    unittest.main()
