from dataclasses import dataclass
from ..nodes.statement_node import Statement


@dataclass
class Assignment(Statement):
    """
    ### location '=' expression ';'
    """

    def __init__(self, location, expression):
        self.type = "Assignment"
        self.location = location
        self.expression = expression
