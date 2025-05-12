from dataclasses import dataclass
from ..nodes.expression_node import Expression


@dataclass
class UnaryOp(Expression):
    """
    ### ('+' / '-' / '^' / '!') expression
    """

    def __init__(self, op, expr):
        self.op = op
        self.expr = expr
