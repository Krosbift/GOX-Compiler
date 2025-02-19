class FileScanner:
    """
    Ejemplo de uso de la clase:
    
    ```python
    # Ruta del archivo
    file_path = "factorize.gox"

    # Leer el archivo como una cadena usando el método estático
    file_content = FileScanner.read_file(file_path)
    ```
    """

    @staticmethod
    def read_file(file_path):
        """
        Lee el contenido de un archivo especificado por el parámetro file_path.

        Args:
            file_path (str): La ruta del archivo a leer.

        Retorna:
            str: El contenido del archivo si se lee correctamente.
            str: Un mensaje de error si el archivo no se encuentra o ocurre otra excepción.
        """
        try:
            with open(file_path, 'r', encoding='utf-8') as file:
                return file.read()
        except FileNotFoundError:
            return "Error: Archivo no encontrado."
        except Exception as e:
            return f"Error: {e}"
