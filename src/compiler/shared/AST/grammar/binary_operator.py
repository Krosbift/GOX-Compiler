from dataclasses import dataclass
from ..nodes.expression_node import Expression


@dataclass
class BinaryOp(Expression):
    """
    ### expression ('||' / '&&' / '<' / '>' / '<=' / '>=' / '==' / '!=' / '+' / '-' / '*' / '/') expression
    """

    def __init__(self, left, op, right):
        self.left = left
        self.op = op
        self.right = right
