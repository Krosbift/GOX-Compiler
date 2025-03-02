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


print(json.dumps(ast_to_dict(ast), indent=4))
