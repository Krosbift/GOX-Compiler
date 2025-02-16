# katherine
class FileToString:
    def __init__(self, file_path):
        self.file_path = file_path

    def read_file(self):
        try:
            with open(self.file_path, 'r', encoding='utf-8') as file:
                return file.read()  # Devuelve el contenido como string
        except FileNotFoundError:
            return "Error: Archivo no encontrado."
        except Exception as e:
            return f"Error: {e}"

# Ruta del archivo
file_path = "factorize.gox"

# Crear instancia y leer el archivo como string
file_reader = FileToString(file_path)
file_content = file_reader.read_file()

# Verificar si se convirtió en string
print(type(file_content))  # Debería imprimir: <class 'str'>
print(file_content)  # Muestra el contenido del archivo
