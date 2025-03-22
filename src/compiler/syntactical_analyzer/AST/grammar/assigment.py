from dataclasses import dataclass
from ..nodes.statement_node import Statement
from ..nodes.expression_node import Expression


@dataclass
class Assigment(Statement):
    """
    ### location '=' expression ';'
    """

    def __init__(self, location: str | Expression, expression: Expression):
        self.location: str | Expression = location
        self.expression: Expression = expression
