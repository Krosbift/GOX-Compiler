from dataclasses import dataclass
from ..nodes.statement_node import Statement


@dataclass
class BinaryOp(Statement):
    """
    ### expression ('||' / '&&' / '<' / '>' / '<=' / '>=' / '==' / '!=' / '+' / '-' / '*' / '/') expression
    """

    def __init__(self, left, op, right):
        self.left = left
        self.op = op
        self.right = right
