from .exceptions.lexical_exception import LexicalException
from .scanner.file_scanner import FileScanner
from .grammar.grammar import Grammar

class LexicalAnalysis:
    """
    Una clase para realizar análisis léxico en un archivo fuente dado.
    Atributos:
    -----------
    file_content : str
        El contenido del archivo fuente a analizar.
    regular_expressions : re.Pattern
        Las expresiones regulares compiladas utilizadas para la coincidencia de tokens.
    Métodos:
    --------
    __init__(file_path):
        Inicializa el análisis léxico con el contenido del archivo en la ruta dada.
    analyze():
        Analiza el contenido del archivo y devuelve una lista de tokens o lanza una LexicalException si se encuentran errores.
    _extract_match_info(match):
        Extrae y devuelve el tipo de token, valor, posición de inicio y posición de fin de un objeto de coincidencia de regex.
    _update_line_info(start_pos, line_start, line_number):
        Actualiza y devuelve el número de línea y la posición de inicio de la línea basada en la posición de inicio del token actual.
    """
    def __init__(self, file_path):
        self.file_content = FileScanner.read_file(file_path)
        self.regular_expressions = Grammar.get_regular_expression()

    def analyze(self):
        """
        Analiza el contenido del archivo usando expresiones regulares para tokenizar la entrada e identificar errores.
        Este método procesa el contenido del archivo línea por línea, usando expresiones regulares para identificar
        diferentes tipos de tokens y errores. Mantiene un seguimiento de los números de línea y columna
        para proporcionar mensajes de error detallados.
        Retorna:
            list: Una lista de tuplas que representan los tokens encontrados en el contenido del archivo. Cada tupla
                  contiene el tipo de token, valor, número de línea y número de columna.
            LexicalException: Si se encuentran errores léxicos, se devuelve una LexicalException
                              que contiene una lista de mensajes de error.
        Lanza:
            LexicalException: Si se encuentran errores léxicos durante el análisis.
        """
        tokens = []
        errores = []
        numero_linea = 1
        inicio_linea = 0

        for match in self.regular_expressions.finditer(self.file_content):
            tipo_token, valor, pos_inicio, pos_fin = self._extract_match_info(match)
            numero_linea, inicio_linea = self._update_line_info(pos_inicio, inicio_linea, numero_linea)
            numero_columna = pos_inicio - inicio_linea

            if tipo_token in ['WHITESPACE', 'NEWLINE', 'COMMENT']:
                continue
            elif tipo_token == 'ERROR':
                errores.append(f"Caracter ilegal: '{valor}' en la línea {numero_linea}, columna {numero_columna}")
            elif tipo_token == 'UNCLOSED_CHAR':
                errores.append(f"Caracter no terminado en la línea {numero_linea}, columna {numero_columna}")
            elif tipo_token == 'UNCLOSED_COMMENT':
                errores.append(f"Comentario no terminado en la línea {numero_linea}, columna {numero_columna}")
            else:
                tokens.append((tipo_token, valor, numero_linea, numero_columna))

        if errores:
            return LexicalException(errores)

        for token in tokens:
            print(token)

        return tokens

    def _extract_match_info(self, match):
        """
        Extrae información de un objeto de coincidencia de regex.

        Args:
            match (re.Match): El objeto de coincidencia de regex.

        Retorna:
            tuple: Una tupla que contiene el tipo de token (str), el valor coincidente (str),
                   la posición de inicio (int) y la posición de fin (int) de la coincidencia.
        """
        tipo_token = match.lastgroup
        valor = match.group(tipo_token)
        pos_inicio = match.start()
        pos_fin = match.end()
        return tipo_token, valor, pos_inicio, pos_fin

    def _update_line_info(self, pos_inicio, inicio_linea, numero_linea):
        """
        Actualiza la información de la línea basada en la posición de inicio dada.

        Este método calcula el número de línea y la posición de inicio de la línea
        basada en la posición de inicio proporcionada dentro del contenido del archivo.

        Args:
            pos_inicio (int): La posición en el contenido del archivo desde la cual comenzar la actualización.
            inicio_linea (int): La posición de inicio de la línea actual.
            numero_linea (int): El número de línea actual.

        Retorna:
            tuple: Una tupla que contiene el número de línea actualizado y la posición de inicio de la línea.
        """
        while inicio_linea < pos_inicio:
            salto_linea = self.file_content.find('\n', inicio_linea, pos_inicio)
            if salto_linea == -1:
                break
            numero_linea += 1
            inicio_linea = salto_linea + 1
        return numero_linea, inicio_linea
