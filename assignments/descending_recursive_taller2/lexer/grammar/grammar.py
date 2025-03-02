TOKEN_REGEX = {
    "NEWLINE": r"\n+",
    "WHITESPACE": r"[ \t]+",
    "NUMBER": r"\d+(\.\d+)?(E[-+]?\d+)?",
    "IDENTIFIER": r"[a-zA-Z_]\w*",
    "ASSIGN": r"=",
    "PLUS": r"\+",
    "MINUS": r"-",
    "TIMES": r"\*",
    "DIVIDE": r"/",
    "SEMICOLON": r";",
    "LPAREN": r"\(",
    "RPAREN": r"\)",
    "ERROR": r".",
}
"""
Este diccionario define las expresiones regulares para los tokens utilizados en el lexer.

TOKEN_REGEX es un diccionario donde las claves son nombres de tokens y los valores son
las expresiones regulares correspondientes.

Tokens:
    - NEWLINE: Coincide con uno o más caracteres de nueva línea.
    - WHITESPACE: Coincide con uno o más espacios o tabulaciones.
    - NUMBER: Coincide con un número entero o de punto flotante, opcionalmente en notación científica.
    - IDENTIFIER: Coincide con un identificador, que comienza con una letra o guion bajo y es seguido por cualquier número de letras, dígitos o guiones bajos.
    - ASSIGN: Coincide con el operador de asignación '='.
    - PLUS: Coincide con el operador de suma '+'.
    - MINUS: Coincide con el operador de resta '-'.
    - TIMES: Coincide con el operador de multiplicación '*'.
    - DIVIDE: Coincide con el operador de división '/'.
    - SEMICOLON: Coincide con el carácter punto y coma ';'.
    - LPAREN: Coincide con el paréntesis izquierdo '('.
    - RPAREN: Coincide con el paréntesis derecho ')'.
    - ERROR: Coincide con cualquier carácter individual (utilizado para el manejo de errores).
"""
