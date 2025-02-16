import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../../')))

import unittest
from unittest.mock import patch, mock_open
from src.lexical_analysis.scanner.file_scanner import FileScanner 

class FileScannerTest(unittest.TestCase):
    def setUp(self):
        self.file_path = "factorize.gox"
        self.file_reader = FileScanner(self.file_path)

    def test_read_file_success(self):
        """ 
        Verifica que el archivo se lea correctamente y devuelva un string 
        """
        mock_content = """
        /* ******************************************************************* *
         *                                                                     *
         * factorize.gox  (compilador gox)                                     *
         *                                                                     *
         * Dado un numero N, lo descompone en sus factores primos.             *
         * Ejemplo: 21 = 3x7                                                   *
         *                                                                     *
         ********************************************************************* *
         */

        func isprime(n int) bool {
            if n < 2 {
                return false;
            }
            var i int = 2;
            while i * i <= n {
                if n % i == 0 {
                    return false;
                }
                i = i + 1;
            }
            return true;
        }

        func factorize(n int) {
            var factor int = 2;
            print "factores primos de " + n + ": ";

            while n > 1 {
                while n % factor == 0 {
                    print factor;
                    n = n / factor;
                }
                factor = factor + 1;
            }
        }

        var num int = 21;
        factorize(num);
        """
        with patch("builtins.open", mock_open(read_data=mock_content)):
            content = self.file_reader.read_file()
            self.assertIsInstance(content, str)
            self.assertTrue(len(content) > 0)

    def test_read_file_not_found(self):
        """ 
        Verifica que se maneje correctamente el caso en que el archivo no se encuentra 
        """
        with patch("builtins.open", side_effect=FileNotFoundError):
            content = self.file_reader.read_file()
            self.assertEqual(content, "Error: Archivo no encontrado.")

    def test_read_file_exception(self):
        """ 
        Verifica que se maneje correctamente cualquier otra excepción 
        """
        with patch("builtins.open", side_effect=Exception("Unexpected error")):
            content = self.file_reader.read_file()
            self.assertTrue(content.startswith("Error:"))

if __name__ == '__main__':
    unittest.main()
