import re
from .grammar.grammar import TOKEN_REGEX


class Lexer:
    def __init__(self, code):
        self.tokens = self.tokenize(code)
        self.pos = 0

    def tokenize(self, code):
        """
        Tokeniza el código fuente dado en una lista de tokens.

        Args:
            code (str): El código fuente a tokenizar.

        Returns:
            list: Una lista de tuplas donde cada tupla contiene el nombre del token y su valor correspondiente.

        La función utiliza expresiones regulares para coincidir con los patrones definidos en TOKEN_REGEX.
        Ignora los tokens que coinciden con "NEWLINE" y "WHITESPACE".
        """
        pattern = "|".join(
            f"(?P<{name}>{regex})" for name, regex in TOKEN_REGEX.items()
        )
        tokens = []
        for match in re.finditer(pattern, code):
            for name, value in match.groupdict().items():
                if value is not None and name not in ["NEWLINE", "WHITESPACE"]:
                    tokens.append((name, value))
        return tokens

    def next_token(self):
        """
        Recupera el siguiente token de la lista de tokens.

        Este método devuelve el siguiente token en la secuencia y avanza el
        contador de posición. Si se alcanza el final de la lista de tokens, devuelve
        un token "EOF".

        Returns:
            tuple: El siguiente token en forma de tupla (tipo_token, valor_token).
                   Si se alcanza el final de la lista de tokens, devuelve ("EOF", "").
        """
        if self.pos < len(self.tokens):
            token = self.tokens[self.pos]
            self.pos += 1
            return token
        return ("EOF", "")

    def peek(self):
        """
        Devuelve el token actual sin avanzar la posición.

        Si la posición actual está dentro de los límites de la lista de tokens,
        devuelve el token en la posición actual. De lo contrario, devuelve
        una tupla que representa el fin de archivo ("EOF", "").

        Returns:
            tuple: El token actual como una tupla (tipo_token, valor_token) o ("EOF", "") si está al final de la lista de tokens.
        """
        if self.pos < len(self.tokens):
            return self.tokens[self.pos]
        return ("EOF", "")
