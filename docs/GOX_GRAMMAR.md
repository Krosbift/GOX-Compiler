# Programa completo
program <- statement* EOF

# Instrucciones del lenguaje
statement <- assignment
           / vardecl
           / funcdecl
           / if_stmt
           / while_stmt
           / break_stmt
           / continue_stmt
           / return_stmt
           / print_stmt

# Asignación de valores
assignment <- location '=' expression ';'

# Declaración de variables
vardecl <- ('var' / 'const') ID type? ('=' expression)? ';'

# Declaración de funciones
funcdecl <- 'import'? 'func' ID '(' parameters ')' type '{' statement* '}'

# Sentencia condicional
if_stmt <- 'if' expression '{' statement* '}'
         / 'if' expression '{' statement* '}' 'else' '{' statement* '}'

# Sentencia de bucle
while_stmt <- 'while' expression '{' statement* '}'

# Sentencias de control de flujo
break_stmt <- 'break' ';'
continue_stmt <- 'continue' ';'
return_stmt <- 'return' expression ';'

# Impresión de valores
print_stmt <- 'print' expression ';'

# Parámetros de funciones
parameters <- ID type (',' ID type)*
            / empty

# Tipos de datos
type <- 'int' / 'float' / 'char' / 'bool'

# Ubicación de valores (variables o direcciones)
location <- ID
          / '`' expression => **Preguntar que significa bien esto**

# Expresiones lógicas y aritméticas
expression <- orterm ('||' orterm)*
orterm <- andterm ('&&' andterm)*
andterm <- relterm (('<' / '>' / '<=' / '>=' / '==' / '!=') relterm)*
relterm <- addterm (('+' / '-') addterm)*
addterm <- factor (('*' / '/') factor)*
factor <- literal  
        / ('+' / '-' / '^') expression
        / '(' expression ')'
        / type '(' expression ')'
        / ID '(' arguments ')'
        / location

# Argumentos de funciones
arguments <- expression (',' expression)*
          / empty

# Valores literales
literal <- INTEGER / FLOAT / CHAR / bool
bool <- 'true' / 'false'