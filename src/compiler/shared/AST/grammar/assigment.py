from dataclasses import dataclass
from ..nodes.statement_node import Statement


@dataclass
class Assignment(Statement):
    """
    ### location '=' expression ';'
    """

    def __init__(self, location, expression):
        self.location = location
        self.expression = expression

    def __repr__(self):
        return f"Assignment(location={self.location!r}, expression={self.expression!r})"
