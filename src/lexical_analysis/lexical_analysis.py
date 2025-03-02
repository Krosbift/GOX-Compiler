from .exceptions.lexical_exception import LexicalException
from .reader.file_reader import FileReader
from .grammar.gox_grammar import Grammar
from .tokens.gox_tokens import Token


class Lexer:
    def __init__(self, file_path):
        self.tokens = []
        self.file_content = FileReader.read(file_path)
        self.regular_expressions = Grammar.get_compiled_regex()

    def analyze(self):
        numero_linea = 1
        inicio_linea = 0

        for match in self.regular_expressions.finditer(self.file_content):
            tipo_token, valor, pos_inicio, pos_fin = self._extract_match_info(match)
            numero_linea, inicio_linea = self._update_line_info(
                pos_inicio, inicio_linea, numero_linea
            )
            numero_columna = pos_inicio - inicio_linea

            if tipo_token in ["WHITESPACE", "NEWLINE", "COMMENT"]:
                continue
            elif tipo_token == "ERROR":
                raise LexicalException(
                    f"Caracter ilegal: '{valor}' en la línea {numero_linea}, columna {numero_columna}"
                )
            elif tipo_token == "UNCLOSED_CHAR":
                raise LexicalException(
                    f"Caracter no terminado en la línea {numero_linea}, columna {numero_columna}"
                )
            elif tipo_token == "UNCLOSED_COMMENT":
                raise LexicalException(
                    f"Comentario no terminado en la línea {numero_linea}, columna {numero_columna}"
                )
            else:
                self.tokens.append(
                    Token(tipo_token, valor, numero_linea, numero_columna)
                )

        return self.tokens

    def _extract_match_info(self, match):
        tipo_token = match.lastgroup
        valor = match.group(tipo_token)
        pos_inicio = match.start()
        pos_fin = match.end()
        return tipo_token, valor, pos_inicio, pos_fin

    def _update_line_info(self, pos_inicio, inicio_linea, numero_linea):
        while inicio_linea < pos_inicio:
            salto_linea = self.file_content.find("\n", inicio_linea, pos_inicio)
            if salto_linea == -1:
                break
            numero_linea += 1
            inicio_linea = salto_linea + 1
        return numero_linea, inicio_linea
