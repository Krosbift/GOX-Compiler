import unittest
from src.lexical_analysis.scanner.file_scanner import FileToString  # Importa tu clase

class TestFileScanner(unittest.TestCase):
    def setUp(self):
        self.file_path = "factorize.gox"
        self.file_reader = FileToString(self.file_path)

    def test_read_file(self):
        """ Verifica que el archivo se lea correctamente y devuelva un string """
        content = self.file_reader.read_file()
        self.assertIsInstance(content, str)  # Comprueba que la salida sea un string
        self.assertTrue(len(content) > 0)  # Asegura que el archivo no esté vacío
        self.assertIn("factorize", content)  # Verifica que contiene la palabra "factorize"

if __name__ == '__main__':
    unittest.main()
