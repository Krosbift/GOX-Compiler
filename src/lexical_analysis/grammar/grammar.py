import re

class Grammar:
    """
    Una clase para definir la gramática para el análisis léxico usando expresiones regulares.
    Atributos:
        REGULAR_EXPRESSIONS (dict): Un diccionario donde las claves son nombres de tokens y los valores son sus patrones de expresiones regulares correspondientes.
    Métodos:
        get_regular_expression():
            Compila las expresiones regulares en un solo patrón con grupos nombrados para cada tipo de token.
            Retorna:
                re.Pattern: Un patrón de expresión regular compilado con grupos nombrados.
    """
    REGULAR_EXPRESSIONS = {
        # Comentarios, espacios y saltos de línea
        'COMMENT': r'//.*|/\*[\s\S]*?\*/',
        'WHITESPACE': r'[ \t]+',
        'NEWLINE': r'\n+',

        # Palabras reservadas
        'CONST': r'\bconst\b', 'VAR': r'\bvar\b', 'PRINT': r'\bprint\b',
        'RETURN': r'\breturn\b', 'BREAK': r'\bbreak\b', 'CONTINUE': r'\bcontinue\b',
        'IF': r'\bif\b', 'ELSE': r'\belse\b', 'WHILE': r'\bwhile\b',
        'FUNC': r'\bfunc\b', 'IMPORT': r'\bimport\b', 'TRUE': r'\btrue\b',
        'FALSE': r'\bfalse\b', 'BOOL': r'\bbool\b', 'INT': r'\bint\b',
        'FLOAT_TYPE': r'\bfloat\b', 'CHAR_TYPE': r'\bchar\b',

        # Operadores
        'PLUS': r'\+', 'MINUS': r'-', 'TIMES': r'\*', 'DIVIDE': r'/',
        'LT': r'<', 'LE': r'<=', 'GT': r'>', 'GE': r'>=',
        'EQ': r'==', 'NE': r'!=', 'LAND': r'&&', 'LOR': r'\|\|', 'GROW': r'\^',

        # Símbolos
        'ASSIGN': r'=', 'SEMI': r';', 'LPAREN': r'\(', 'RPAREN': r'\)',
        'LBRACE': r'\{', 'RBRACE': r'\}', 'COMMA': r',', 'DEREF': r'`',

        # Literales
        'FLOAT': r'\d*\.\d+|\d+\.', 
        'INTEGER': r'\d+',
        'CHAR': r"'(\\x[0-9a-fA-F]{2}|\\.|[^\\'])'",
        'ID': r'[a-zA-Z_][a-zA-Z_0-9]*',

        # errores
        'ERROR': r'.',
        'UNCLOSED_CHAR': r"'",
        'UNCLOSED_COMMENT': r'/\*',
    }

    @staticmethod
    def get_regular_expression():
        """
        Construye y compila un patrón de expresión regular a partir de las
        expresiones regulares definidas en la clase Grammar.

        El método une todas las expresiones regulares definidas en Grammar.REGULAR_EXPRESSIONS
        en un solo patrón, donde cada patrón nombrado está envuelto en un grupo de captura nombrado.

        Retorna:
            re.Pattern: Un objeto de expresión regular compilado que se puede usar para hacer coincidir.
        """
        regex = '|'.join(f'(?P<{name}>{pattern})' for name, pattern in Grammar.REGULAR_EXPRESSIONS.items())
        return re.compile(regex)
