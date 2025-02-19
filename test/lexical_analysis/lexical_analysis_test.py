import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')))

import unittest
from unittest.mock import patch, MagicMock
from src.lexical_analysis.lexical_analysis import LexicalAnalysis
from src.lexical_analysis.exceptions.lexical_exception import LexicalException

class TestLexicalAnalysis(unittest.TestCase):
    @patch('src.lexical_analysis.lexical_analysis.FileScanner.read_file')
    @patch('src.lexical_analysis.lexical_analysis.Grammar.get_regular_expression')
    def test_analyze_valid_tokens(self, mock_get_regular_expression, mock_read_file):
        mock_read_file.return_value = 'valid content'
        mock_regex = MagicMock()
        mock_regex.finditer.return_value = [
            MagicMock(lastgroup='IDENTIFIER', group=lambda x: 'valid', start=lambda: 0, end=lambda: 5)
        ]
        mock_get_regular_expression.return_value = mock_regex

        lexical_analysis = LexicalAnalysis('../../factorize.gox')
        tokens = lexical_analysis.analyze()

        self.assertEqual(tokens, [('IDENTIFIER', 'valid', 1, 0)])

if __name__ == '__main__':
    unittest.main()