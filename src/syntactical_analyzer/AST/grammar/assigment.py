from dataclasses import dataclass, field
from ..nodes.statement_node import Statement
from ..nodes.expression_node import Expression


@dataclass
class Assigment(Statement):
    """
    ### location '=' expression ';'
    """

    location: str | Expression
    expression: Expression
