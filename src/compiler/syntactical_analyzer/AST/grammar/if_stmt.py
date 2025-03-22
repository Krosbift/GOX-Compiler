from dataclasses import dataclass
from ..nodes.statement_node import Statement


@dataclass
class IfStmt(Statement):
    def __init__(self, condition, then_block, else_block):
        self.condition = condition
        self.then_block = then_block
        self.else_block = else_block
