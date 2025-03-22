from dataclasses import dataclass
from ..nodes.statement_node import Statement


@dataclass
class PrintStmt(Statement):
    def __init__(self, expression):
        self.expression = expression
