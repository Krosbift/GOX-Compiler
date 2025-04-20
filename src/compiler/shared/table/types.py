# semantic/types.py

# Tipos básicos (puedes usar constantes o una clase Enum)
TYPE_INT = "int"
TYPE_FLOAT = "float"
TYPE_BOOL = "bool"
TYPE_CHAR = "char"
TYPE_VOID = "void"  # Para funciones que no retornan nada (si aplica)
TYPE_ERROR = "error"  # Para indicar un error de tipo

# Mapeo de nombres de token/AST a tipos internos
TYPE_MAP = {
    "INT": TYPE_INT,
    "INTEGER": TYPE_INT,
    "FLOAT_TYPE": TYPE_FLOAT,
    "FLOAT": TYPE_FLOAT,
    "CHAR_TYPE": TYPE_CHAR,
    "CHAR": TYPE_CHAR,
    "BOOL": TYPE_BOOL,
    "TRUE": TYPE_BOOL,
    "FALSE": TYPE_BOOL,
}


def get_type_from_name(name: str) -> str:
    """Convierte un nombre de tipo (string) a nuestro tipo interno."""
    return TYPE_MAP.get(
        name.upper(), name
    )  # Devuelve el tipo mapeado o el mismo nombre si no está


def is_numeric(type_name: str) -> bool:
    return type_name in [TYPE_INT, TYPE_FLOAT]


def is_boolean(type_name: str) -> bool:
    return type_name == TYPE_BOOL


def is_compatible_for_assignment(target_type: str, source_type: str) -> bool:
    """Verifica si source_type puede ser asignado a target_type."""
    if target_type == source_type:
        return True
    # Permitir asignar int a float (coerción implícita)
    if target_type == TYPE_FLOAT and source_type == TYPE_INT:
        return True
    # Añade más reglas de compatibilidad según tu lenguaje
    # Ejemplo: ¿Se puede asignar char a int? ¿bool a int?
    return False


def check_binary_op_type(op: str, left_type: str, right_type: str) -> str:
    """Determina el tipo resultante de una operación binaria."""
    if left_type == TYPE_ERROR or right_type == TYPE_ERROR:
        return TYPE_ERROR

    # Operaciones aritméticas (+, -, *, /)
    if op in ["+", "-", "*", "/"]:
        if is_numeric(left_type) and is_numeric(right_type):
            # Promoción a float si uno de los operandos es float
            if left_type == TYPE_FLOAT or right_type == TYPE_FLOAT:
                return TYPE_FLOAT
            else:
                return TYPE_INT
        else:
            return TYPE_ERROR  # Operación aritmética en tipos no numéricos

    # Operaciones relacionales (<, >, <=, >=, ==, !=)
    elif op in ["<", ">", "<=", ">=", "==", "!="]:
        # Permitir comparación entre numéricos
        if is_numeric(left_type) and is_numeric(right_type):
            return TYPE_BOOL
        # Permitir comparación entre booleanos (==, !=)
        elif op in ["==", "!="] and is_boolean(left_type) and is_boolean(right_type):
            return TYPE_BOOL
        # Permitir comparación entre chars (==, !=, y tal vez <, > etc.)
        elif left_type == TYPE_CHAR and right_type == TYPE_CHAR:
            return TYPE_BOOL
        else:
            # Comparación entre tipos incompatibles
            return TYPE_ERROR

    # Operaciones lógicas (&&, ||)
    elif op in ["&&", "||"]:
        if is_boolean(left_type) and is_boolean(right_type):
            return TYPE_BOOL
        else:
            return TYPE_ERROR  # Operación lógica en tipos no booleanos

    # Operador GROW ('^') - ¿Exponenciación? ¿Bitwise XOR? Asumamos exponenciación por ahora
    elif op == "^":
        if is_numeric(left_type) and is_numeric(right_type):
            if left_type == TYPE_FLOAT or right_type == TYPE_FLOAT:
                return TYPE_FLOAT
            else:
                return TYPE_INT
        else:
            return TYPE_ERROR

    return TYPE_ERROR  # Operador desconocido o combinación inválida


def check_unary_op_type(op: str, operand_type: str) -> str:
    """Determina el tipo resultante de una operación unaria."""
    if operand_type == TYPE_ERROR:
        return TYPE_ERROR

    if op == "-":  # Negación aritmética
        if is_numeric(operand_type):
            return operand_type
        else:
            return TYPE_ERROR
    elif op == "+":  # Más unario
        if is_numeric(operand_type):
            return operand_type
        else:
            return TYPE_ERROR
    # Añadir '!' para negación lógica si tu lenguaje lo soporta
    # elif op == '!':
    #     if is_boolean(operand_type):
    #         return TYPE_BOOL
    #     else:
    #         return TYPE_ERROR
    elif op == "^":  # GROW como operador unario? El parser lo tiene en primary.
        # Si ^ es "obtener dirección", necesitaríamos tipos puntero.
        # Si es otra cosa (¿bitwise not?), define la regla aquí.
        # Por ahora, marcamos como error hasta aclarar su semántica unaria.
        return TYPE_ERROR
    # Añadir '`' (DEREF) si fuera unario - aunque el parser lo usa en `location`
    # elif op == '`': # Dereferencia
    #     if is_pointer(operand_type): # Necesitarías una función is_pointer
    #         return get_base_type(operand_type) # Necesitarías una función get_base_type
    #     else:
    #         return TYPE_ERROR

    return TYPE_ERROR  # Operador unario desconocido o tipo inválido
