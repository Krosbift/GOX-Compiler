from dataclasses import dataclass
from ..nodes.statement_node import Statement


@dataclass
class FunctionCall(Statement):
    """
    ### ID '(' arguments ')'
    """

    def __init__(self, name, arguments):
        self.name = name
        self.arguments = arguments

    def __repr__(self):
        return f"FunctionCall(name={self.name!r}, arguments={self.arguments!r})"
