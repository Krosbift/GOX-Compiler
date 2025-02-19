import sys
import os
from lexical_analysis.grammar.grammar import Grammar

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../../')))

import unittest
import re

class GrammarTest(unittest.TestCase):
  def test_comment(self):
    pattern = re.compile(Grammar.REGULAR_EXPRESSIONS['COMMENT'])
    self.assertTrue(pattern.match('// this is a comment'))
    self.assertTrue(pattern.match('/* this is a \n multiline comment */'))

  def test_float(self):
    pattern = re.compile(Grammar.REGULAR_EXPRESSIONS['FLOAT'])
    self.assertTrue(pattern.match('3.14'))
    self.assertTrue(pattern.match('0.5'))
    self.assertTrue(pattern.match('10.'))

  def test_integer(self):
    pattern = re.compile(Grammar.REGULAR_EXPRESSIONS['INTEGER'])
    self.assertTrue(pattern.match('42'))
    self.assertTrue(pattern.match('0'))

  def test_char(self):
    pattern = re.compile(Grammar.REGULAR_EXPRESSIONS['CHAR'])
    self.assertTrue(pattern.match("'a'"))
    self.assertTrue(pattern.match("'\\n'"))
    self.assertTrue(pattern.match("'\\x41'"))

  def test_id(self):
    pattern = re.compile(Grammar.REGULAR_EXPRESSIONS['ID'])
    self.assertTrue(pattern.match('variable'))
    self.assertTrue(pattern.match('_var123'))

  def test_reserved_words(self):
    reserved_words = ['const', 'var', 'print', 'return', 'break', 'continue', 'if', 'else', 'while', 'func', 'import', 'true', 'false']
    for word in reserved_words:
      pattern = re.compile(Grammar.REGULAR_EXPRESSIONS[word.upper()])
      self.assertTrue(pattern.match(word))

  def test_operators(self):
    operators = {
      'PLUS': '+', 'MINUS': '-', 'TIMES': '*', 'DIVIDE': '/',
      'LT': '<', 'LE': '<=', 'GT': '>', 'GE': '>=',
      'EQ': '==', 'NE': '!=', 'LAND': '&&', 'LOR': '||', 'GROW': '^'
    }
    for op, symbol in operators.items():
      pattern = re.compile(Grammar.REGULAR_EXPRESSIONS[op])
      self.assertTrue(pattern.match(symbol))

  def test_symbols(self):
    symbols = {
      'ASSIGN': '=', 'SEMI': ';', 'LPAREN': '(', 'RPAREN': ')',
      'LBRACE': '{', 'RBRACE': '}', 'COMMA': ',', 'DEREF': '`'
    }
    for sym, symbol in symbols.items():
      pattern = re.compile(Grammar.REGULAR_EXPRESSIONS[sym])
      self.assertTrue(pattern.match(symbol))

  def test_whitespace(self):
    pattern = re.compile(Grammar.REGULAR_EXPRESSIONS['WHITESPACE'])
    self.assertTrue(pattern.match(' '))
    self.assertTrue(pattern.match('\t'))

  def test_newline(self):
    pattern = re.compile(Grammar.REGULAR_EXPRESSIONS['NEWLINE'])
    self.assertTrue(pattern.match('\n'))
    self.assertTrue(pattern.match('\n\n'))

  def test_error(self):
    pattern = re.compile(Grammar.REGULAR_EXPRESSIONS['ERROR'])
    self.assertTrue(pattern.match('@'))
    self.assertTrue(pattern.match('#'))

if __name__ == '__main__':
  unittest.main()
