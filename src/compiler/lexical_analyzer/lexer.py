from ...shared.reader.file_reader import FileReader
from ...shared.grammar.gox_grammar import Grammar
from ...shared.grammar.gox_token import Token
from .exceptions.lexer_error import LexerError


class Lexer:
    def __init__(self, file_path):
        self.errors = []
        self.tokens = []
        self.file_content = FileReader.read(file_path)
        self.regular_expressions = Grammar.get_compiled_regex()

    def analyze(self):
        line_number = 1
        line_start = 0

        for match in self.regular_expressions.finditer(self.file_content):
            token_type, value, start_pos, end_pos = self._extract_match_info(match)
            line_number, line_start = self._update_line_info(
                start_pos, line_start, line_number
            )
            column_number = start_pos - line_start

            if token_type in ["WHITESPACE", "NEWLINE", "COMMENT"]:
                continue
            elif token_type in ["ERROR", "UNCLOSED_CHAR", "UNCLOSED_COMMENT"]:
                self._handle_error(token_type, value, line_number, column_number)
            else:
                self.tokens.append(Token(token_type, value, line_number, column_number))

        if self.errors:
            raise LexerError(self.errors)

        return self.tokens

    def _extract_match_info(self, match):
        token_type = match.lastgroup
        value = match.group(token_type)
        start_pos = match.start()
        end_pos = match.end()
        return token_type, value, start_pos, end_pos

    def _update_line_info(self, start_pos, line_start, line_number):
        while line_start < start_pos:
            newline_pos = self.file_content.find("\n", line_start, start_pos)
            if newline_pos == -1:
                break
            line_number += 1
            line_start = newline_pos + 1
        return line_number, line_start

    def _handle_error(self, token_type, value, line_number, column_number):
        error_messages = {
            "ERROR": f"Caracter ilegal: '{value}' en la línea {line_number}, columna {column_number}",
            "UNCLOSED_CHAR": f"Caracter no terminado en la línea {line_number}, columna {column_number}",
            "UNCLOSED_COMMENT": f"Comentario no terminado en la línea {line_number}, columna {column_number}",
        }
        self.errors.append(
            (
                Token(token_type, value, line_number, column_number),
                error_messages[token_type],
            )
        )
