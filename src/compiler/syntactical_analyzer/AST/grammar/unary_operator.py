from dataclasses import dataclass
from ..nodes.statement_node import Statement


@dataclass
class UnaryOp(Statement):
    def __init__(self, op, expr):
        self.op = op
        self.expr = expr