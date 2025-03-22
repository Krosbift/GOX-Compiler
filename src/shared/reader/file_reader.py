class FileReader:
    @staticmethod
    def read(file_path: str):
        try:
            with open(file_path, "r", encoding="utf-8") as file:
                return file.read()
        except FileNotFoundError:
            raise FileNotFoundError("Error: Archivo no encontrado.")
        except Exception as error:
            raise Exception(error)
