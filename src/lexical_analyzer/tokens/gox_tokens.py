class Token:
    """
    Una clase utilizada para representar un Token en el análisis léxico.
    Atributos
    ---------
    type : str
        El tipo de token (por ejemplo, identificador, palabra clave, operador).
    value : str
        El valor del token (por ejemplo, el nombre real del identificador, texto de la palabra clave, símbolo del operador).
    line : int
        El número de línea donde se encuentra el token en el código fuente.
    column : int
        El número de columna donde comienza el token en el código fuente.
    Métodos
    -------
    __str__():
        Devuelve una representación en cadena del token.
    """

    def __init__(self, type, value, line, column):
        self.type = type
        self.value = value
        self.line = line
        self.column = column

    def __str__(self):
        return f"Token({self.type}, {repr(self.value)}, {self.line}, {self.column})"
