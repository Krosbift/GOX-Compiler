import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../../")))

import json
from assignments.descending_recursive_taller2.lexer.lexer import Lexer
from assignments.descending_recursive_taller2.parser.parser import (
    Parser,
    Program,
    Assignment,
    Expression,
    BinaryOperation,
    Number,
    Identifier,
)


code = """
    a = 1 + 2 * 3 / 4 - 5;
    a * 78;
    b = 14 / 35;
    - (a * b);
"""
lexer = Lexer(code)
parser = Parser(lexer)
ast = parser.parse()


def ast_to_dict(node):
    """
    Convert an Abstract Syntax Tree (AST) node into a dictionary representation.

    Args:
        node: The AST node to convert. This can be an instance of Program, Assignment,
              Expression, BinaryOperation, Number, or Identifier.

    Returns:
        A dictionary representation of the AST node. The structure of the dictionary
        depends on the type of the node:
        - Program: {"Program": [list of statements as dictionaries]}
        - Assignment: {"Assignment": {"identifier": identifier name, "expression": expression as dictionary}}
        - Expression: {"Expression": expression value as dictionary}
        - BinaryOperation: {"BinaryOperation": {"left": left operand as dictionary, "operator": operator, "right": right operand as dictionary}}
        - Number: {"Number": number value}
        - Identifier: {"Identifier": identifier name}
        - If the node type is unknown, returns "Unknown Node".
    """
    if isinstance(node, Program):
        return {"Program": [ast_to_dict(stmt) for stmt in node.statements]}
    elif isinstance(node, Assignment):
        return {
            "Assignment": {
                "identifier": node.identifier.name,
                "expression": ast_to_dict(node.expression),
            }
        }
    elif isinstance(node, Expression):
        return {"Expression": ast_to_dict(node.value)}
    elif isinstance(node, BinaryOperation):
        return {
            "BinaryOperation": {
                "left": ast_to_dict(node.left),
                "operator": node.operator,
                "right": ast_to_dict(node.right),
            }
        }
    elif isinstance(node, Number):
        return {"Number": node.value}
    elif isinstance(node, Identifier):
        return {"Identifier": node.name}
    return "Unknown Node"


print(json.dumps(ast_to_dict(ast), indent=2))
