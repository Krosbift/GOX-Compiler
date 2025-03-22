from dataclasses import dataclass
from ..nodes.statement_node import Statement


@dataclass
class FunctionCall(Statement):
    """
    ### ID '(' arguments ')'
    """

    def __init__(self, name, arguments):
        self.type = "FunctionCall"
        self.name = name
        self.arguments = arguments
