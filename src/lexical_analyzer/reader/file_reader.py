class FileReader:
    """
    FileScanner es una clase de utilidad para leer el contenido de archivos.
    """

    @staticmethod
    def read(file_path: str):
        """
        Lee el contenido de un archivo y lo devuelve como una cadena.

        Args:
            file_path (str): La ruta al archivo que se va a leer.

        Returns:
            str: El contenido del archivo.

        Raises:
            FileNotFoundError: Si el archivo no se encuentra en la ruta especificada.
            Exception: Si ocurre cualquier otro error durante la lectura del archivo.
        """
        try:
            with open(file_path, "r", encoding="utf-8") as file:
                return file.read()
        except FileNotFoundError:
            raise FileNotFoundError("Error: Archivo no encontrado.")
        except Exception as error:
            raise Exception(error)
