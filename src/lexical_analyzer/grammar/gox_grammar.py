import re


class Grammar:
    """
    Una clase para definir la gramática y las especificaciones de tokens para el análisis léxico del compilador GOX.
    Atributos:
        TOKEN_SPECS (lista de tuplas): Una lista de tuplas donde cada tupla contiene un nombre de token y su correspondiente patrón regex.
    Métodos:
        get_compiled_regex():
            Compila las especificaciones de tokens en un solo patrón regex con grupos nombrados para cada tipo de token.
            Retorna:
                re.Pattern: Un patrón regex compilado que se puede usar para coincidir tokens en el código fuente.
    """

    TOKEN_SPECS = [
        ("NEWLINE", r"\n+"),
        ("WHITESPACE", r"[ \t]+"),
        ("COMMENT", r"/\*[^*]*\*+(?:[^/*][^*]*\*+)*/|//[^\n]*"),
        ("LE", r"<="),
        ("GE", r">="),
        ("EQ", r"=="),
        ("NE", r"!="),
        ("LAND", r"&&"),
        ("LOR", r"\|\|"),
        ("LT", r"<"),
        ("GT", r">"),
        ("PLUS", r"\+"),
        ("MINUS", r"-"),
        ("GROW", r"\^"),
        ("TIMES", r"\*"),
        ("DIVIDE", r"/"),
        ("ASSIGN", r"="),
        ("SEMI", r";"),
        ("COMMA", r","),
        ("DEREF", r"`"),
        ("LPAREN", r"\("),
        ("RPAREN", r"\)"),
        ("LBRACE", r"\{"),
        ("RBRACE", r"\}"),
        ("IF", r"\bif\b"),
        ("INT", r"\bint\b"),
        ("VAR", r"\bvar\b"),
        ("TRUE", r"\btrue\b"),
        ("FUNC", r"\bfunc\b"),
        ("ELSE", r"\belse\b"),
        ("BOOL", r"\bbool\b"),
        ("FALSE", r"\bfalse\b"),
        ("BREAK", r"\bbreak\b"),
        ("CONST", r"\bconst\b"),
        ("PRINT", r"\bprint\b"),
        ("WHILE", r"\bwhile\b"),
        ("RETURN", r"\breturn\b"),
        ("IMPORT", r"\bimport\b"),
        ("CHAR_TYPE", r"\bchar\b"),
        ("FLOAT_TYPE", r"\bfloat\b"),
        ("CONTINUE", r"\bcontinue\b"),
        ("CHAR", r"'(\\[nrt'\"\\]|x[0-9a-fA-F]{2}|[^'\\])'"),
        ("FLOAT", r"\d+\.\d+"),
        ("INTEGER", r"\d+"),
        ("ID", r"[a-zA-Z_][a-zA-Z0-9_]*"),
        ("UNCLOSED_COMMENT", r"/\*.*"),
        ("UNCLOSED_CHAR", r"'(?:\\.|[^'\\])*"),
        ("ERROR", r"."),
    ]

    @staticmethod
    def get_compiled_regex():
        """
        Compila las especificaciones de tokens en un solo patrón de expresión regular.

        Este método construye un patrón regex uniendo todas las especificaciones de tokens
        definidas en `Grammar.TOKEN_SPECS` con un grupo nombrado para cada token. El
        patrón resultante se compila en un objeto regex.

        Retorna:
            re.Pattern: Un objeto de expresión regular compilado que se puede usar para
            coincidir tokens en el texto de entrada.
        """
        regex_pattern = "|".join(
            f"(?P<{name}>{pattern})" for name, pattern in Grammar.TOKEN_SPECS
        )
        return re.compile(regex_pattern)
