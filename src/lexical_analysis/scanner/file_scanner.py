class FileScanner:
    """
    Ejemplo de uso de la clase:
    
    ```python
    # Ruta del archivo
    file_path = "factorize.gox"

    # Crear instancia y leer el archivo como una cadena
    file_reader = FileToString(file_path)
    file_content = file_reader.read_file()
    ```
    """

    def __init__(self, file_path):
        self.file_path = file_path

    def read_file(self):
        """
        Lee el contenido de un archivo especificado por el atributo file_path.

        Retorna:
            str: El contenido del archivo si se lee correctamente.
            str: Un mensaje de error si el archivo no se encuentra o ocurre otra excepción.
        """
        try:
            with open(self.file_path, 'r', encoding='utf-8') as file:
                return file.read()
        except FileNotFoundError:
            return "Error: Archivo no encontrado."
        except Exception as e:
            return f"Error: {e}"
