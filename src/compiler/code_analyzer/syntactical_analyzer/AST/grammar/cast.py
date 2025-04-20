from dataclasses import dataclass
from ..nodes.expression_node import Expression


@dataclass
class Cast(Expression):
    """
    ### type '(' expression ')'
    """

    def __init__(self, cast_type, expression):
        self.cast_type = cast_type
        self.expression = expression
