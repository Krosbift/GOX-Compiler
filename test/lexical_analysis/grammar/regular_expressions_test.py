import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../../')))


import unittest
from unittest.mock import patch, mock_open
from src.lexical_analysis.grammar.grammar import TOKEN_SPECS

class TestTokenizer(unittest.TestCase):
  """
  Unit tests for the Tokenizer class.
  This module contains a unit test for the Tokenizer class, specifically testing
  the tokenization of a simple input string.
  Classes:
    TestTokenizer: A unittest.TestCase subclass that contains the test for the
    Tokenizer class.
  Methods:
    test_simple_tokens: Tests the tokenization of a simple input string and
    verifies that the generated tokens match the expected tokens.
  """

  def test_simple_tokens(self):
    text = "var x = 42; print(x);"
    print(text)
    tokens = [tok for tok in TOKEN_SPECS(text)]
    
    expected_tokens = [
      TOKEN_SPECS(type='VAR', value='var', lineno=1),
      TOKEN_SPECS(type='ID', value='x', lineno=1),
      TOKEN_SPECS(type='ASSIGN', value='=', lineno=1),
      TOKEN_SPECS(type='INTEGER', value='42', lineno=1),
      TOKEN_SPECS(type='SEMI', value=';', lineno=1),
      TOKEN_SPECS(type='PRINT', value='print', lineno=1),
      TOKEN_SPECS(type='LPAREN', value='(', lineno=1),
      TOKEN_SPECS(type='ID', value='x', lineno=1),
      TOKEN_SPECS(type='RPAREN', value=')', lineno=1),
      TOKEN_SPECS(type='SEMI', value=';', lineno=1),
    ]
    
    self.assertEqual(tokens, expected_tokens)
		
if __name__ == '__main__':
	unittest.main()
