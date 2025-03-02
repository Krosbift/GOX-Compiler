from .exceptions.lexical_exception import LexicalException
from .reader.file_reader import FileReader
from .grammar.gox_grammar import Grammar
from .tokens.gox_tokens import Token


class Lexer:
    """
    Clase Lexer para el análisis léxico de archivos de entrada.
    Esta clase lee el contenido de un archivo, utiliza expresiones regulares para tokenizar la entrada,
    y maneja varios tipos de tokens, incluyendo espacios en blanco, nuevas líneas, comentarios y errores.
    Lanza excepciones para caracteres ilegales, caracteres no terminados y comentarios no terminados.
    Atributos:
        tokens (List[Token]): Una lista para almacenar los tokens extraídos del contenido del archivo.
        file_content (str): El contenido del archivo a ser analizado.
        regular_expressions (Pattern): Las expresiones regulares compiladas para tokenizar la entrada.
    Métodos:
        __init__(file_path):
            Inicializa el Lexer con la ruta del archivo dada, lee el contenido del archivo y compila las expresiones regulares.
    """

    def __init__(self, file_path):
        self.tokens = []
        self.file_content = FileReader.read(file_path)
        self.regular_expressions = Grammar.get_compiled_regex()

    def analyze(self):
        """
        Analiza el contenido del archivo utilizando expresiones regulares para tokenizar la entrada.
        Este método itera sobre las coincidencias encontradas por las expresiones regulares y
        extrae información de los tokens como tipo, valor, posición de inicio y posición de fin.
        Actualiza la información de línea y columna en consecuencia y agrega tokens válidos
        a la lista de tokens. Lanza excepciones para caracteres ilegales, caracteres no terminados
        y comentarios no terminados.
        Lanza:
            LexicalException: Si se encuentra un carácter ilegal, un carácter no terminado o un comentario no terminado.
        Retorna:
            List[Token]: Una lista de tokens extraídos del contenido del archivo.
        """
        numero_linea = 1
        inicio_linea = 0

        for match in self.regular_expressions.finditer(self.file_content):
            tipo_token, valor, pos_inicio, pos_fin = self._extract_match_info(match)
            numero_linea, inicio_linea = self._update_line_info(
                pos_inicio, inicio_linea, numero_linea
            )
            numero_columna = pos_inicio - inicio_linea

            if tipo_token in ["WHITESPACE", "NEWLINE", "COMMENT"]:
                continue
            elif tipo_token == "ERROR":
                raise LexicalException(
                    f"Caracter ilegal: '{valor}' en la línea {numero_linea}, columna {numero_columna}"
                )
            elif tipo_token == "UNCLOSED_CHAR":
                raise LexicalException(
                    f"Caracter no terminado en la línea {numero_linea}, columna {numero_columna}"
                )
            elif tipo_token == "UNCLOSED_COMMENT":
                raise LexicalException(
                    f"Comentario no terminado en la línea {numero_linea}, columna {numero_columna}"
                )
            else:
                self.tokens.append(
                    Token(tipo_token, valor, numero_linea, numero_columna)
                )

        return self.tokens

    def _extract_match_info(self, match):
        """
        Extrae información de un objeto de coincidencia de regex.

        Args:
            match (re.Match): El objeto de coincidencia de regex.

        Returns:
            tuple: Una tupla que contiene:
            - tipo_token (str): El tipo del token.
            - valor (str): El valor del token.
            - pos_inicio (int): La posición de inicio de la coincidencia.
            - pos_fin (int): La posición de fin de la coincidencia.
        """
        tipo_token = match.lastgroup
        valor = match.group(tipo_token)
        pos_inicio = match.start()
        pos_fin = match.end()
        return tipo_token, valor, pos_inicio, pos_fin

    def _update_line_info(self, pos_inicio, inicio_linea, numero_linea):
        """
        Actualiza la información de la línea basada en la posición de inicio dada.

        Este método incrementa el número de línea y actualiza la posición de inicio de la línea
        escaneando los caracteres de nueva línea en el contenido del archivo desde la
        posición actual de inicio de la línea hasta la posición de inicio dada.

        Args:
            pos_inicio (int): La posición hasta la cual se debe actualizar la información de la línea.
            inicio_linea (int): La posición actual de inicio de la línea.
            numero_linea (int): El número de línea actual.

        Returns:
            tuple: Una tupla que contiene el número de línea actualizado y la posición de inicio de la línea actualizada.
        """
        while inicio_linea < pos_inicio:
            salto_linea = self.file_content.find("\n", inicio_linea, pos_inicio)
            if salto_linea == -1:
                break
            numero_linea += 1
            inicio_linea = salto_linea + 1
        return numero_linea, inicio_linea
