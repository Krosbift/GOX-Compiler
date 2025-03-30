from dataclasses import dataclass
from ..nodes.statement_node import Statement


@dataclass
class Cast(Statement):
    """
    ### type '(' expression ')'
    """

    def __init__(self, cast_type, expression):
        self.cast_type = cast_type
        self.expression = expression
