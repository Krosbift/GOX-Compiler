import re

# Define the tokens
TOKEN_SPECS = [
    ('COMMENT',    r'//.*|/\*[\s\S]*?\*/'),  # Comentarios
    ('FLOAT',      r'\d*\.\d+|\d+\.'),       # Números flotantes
    ('INTEGER',    r'\d+'),                  # Números enteros
    ('CHAR',       r"'.'|'\\.'|'\\x[0-9A-Fa-f]{2}'"),  # Caracteres
    ('ID',         r'[a-zA-Z_][a-zA-Z_0-9]*'),  # Identificadores

    # Reserved words
    ('CONST',      r'const'), ('VAR', r'var'), ('PRINT', r'print'),
    ('RETURN',     r'return'), ('BREAK', r'break'), ('CONTINUE', r'continue'),
    ('IF',         r'if'), ('ELSE', r'else'), ('WHILE', r'while'),
    ('FUNC',       r'func'), ('IMPORT', r'import'), ('TRUE', r'true'),
    ('FALSE',      r'false'),

    # Operators
    ('PLUS',       r'\+'), ('MINUS', r'-'), ('TIMES', r'\*'), ('DIVIDE', r'/'),
    ('LT',         r'<'), ('LE', r'<='), ('GT', r'>'), ('GE', r'>='),
    ('EQ',         r'=='), ('NE', r'!='), ('LAND', r'&&'), ('LOR', r'\|\|'), ('GROW', r'\^'),

    # Symbols
    ('ASSIGN',     r'='), ('SEMI', r';'), ('LPAREN', r'\('), ('RPAREN', r'\)'),
    ('LBRACE',     r'\{'), ('RBRACE', r'\}'), ('COMMA', r','), ('DEREF', r'`'),

    # Spaces and line breaks
    ('NEWLINE',    r'\n+'),
    ('WHITESPACE', r'[ \t]+'),

    # Errors
    ('ERROR',      r'.')  # Cualquier otro carácter se marcará como error
]
