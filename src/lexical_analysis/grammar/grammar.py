class Grammar:
    REGULAR_EXPRESSIONS = {
        # Comentarios, números, caracteres e identificadores
        'COMMENT': r'//.*|/\*[\s\S]*?\*/',
        'FLOAT': r'\d*\.\d+|\d+\.', 
        'INTEGER': r'\d+',
        'CHAR': r"'.'|'\\.'|'\\x[0-9A-Fa-f]{2}'",
        'ID': r'[a-zA-Z_][a-zA-Z_0-9]*',

        # Palabras reservadas
        'CONST': r'const', 'VAR': r'var', 'PRINT': r'print',
        'RETURN': r'return', 'BREAK': r'break', 'CONTINUE': r'continue',
        'IF': r'if', 'ELSE': r'else', 'WHILE': r'while',
        'FUNC': r'func', 'IMPORT': r'import', 'TRUE': r'true',
        'FALSE': r'false',

        # Operadores
        'PLUS': r'\+', 'MINUS': r'-', 'TIMES': r'\*', 'DIVIDE': r'/',
        'LT': r'<', 'LE': r'<=', 'GT': r'>', 'GE': r'>=',
        'EQ': r'==', 'NE': r'!=', 'LAND': r'&&', 'LOR': r'\|\|', 'GROW': r'\^',

        # Símbolos
        'ASSIGN': r'=', 'SEMI': r';', 'LPAREN': r'\(', 'RPAREN': r'\)',
        'LBRACE': r'\{', 'RBRACE': r'\}', 'COMMA': r',', 'DEREF': r'`',

        # Espacios y saltos de línea
        'NEWLINE': r'\n+',
        'WHITESPACE': r'[ \t]+',

        # Cualquier otro carácter se marcará como error
        'ERROR': r'.'
    }
