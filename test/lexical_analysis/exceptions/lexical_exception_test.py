import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../../')))

import unittest
from io import StringIO
from src.lexical_analysis.exceptions.lexical_exception import LexicalException

class LexicalExceptionTest(unittest.TestCase):
    def test_format_errors(self):
        errors = ["Error 1", "Error 2"]
        expected_output = "Errores de compilación:\nError 1\nError 2\n"
        
        captured_output = StringIO()
        sys.stdout = captured_output
        
        exception = LexicalException(errors)
        
        sys.stdout = sys.__stdout__
        
        self.assertEqual(captured_output.getvalue(), expected_output)

if __name__ == '__main__':
    unittest.main()
