import re


class Grammar:
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
        ("MEMORY_ADDRESS", r"'\\x[0-9a-fA-F]{2}'"),
        ("ERROR", r"."),
    ]

    @staticmethod
    def get_compiled_regex():
        regex_pattern = "|".join(
            f"(?P<{name}>{pattern})" for name, pattern in Grammar.TOKEN_SPECS
        )
        return re.compile(regex_pattern)
