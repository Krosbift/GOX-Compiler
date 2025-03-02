class LexicalException:
    """
    Una clase utilizada para representar una Excepción Léxica.
    Atributos
    ---------
    errors : str
        Una cadena que contiene los errores de compilación formateados.
    Métodos
    -------
    __init__(errors)
        Inicializa la LexicalException con una lista de errores y los formatea.
    format_errors()
    """

    def __init__(self, errors):
        self.errors = "".join(errors)
        self.format_errors()

    def format_errors(self):
        """
        Formatea e imprime los errores de compilación.

        Este método imprime un encabezado "Errores de compilación:" seguido de la lista de errores almacenados en el atributo `self.errors`.
        """
        print("Errores de compilación:")
        print(self.errors)
