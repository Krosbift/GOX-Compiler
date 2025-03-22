from dataclasses import dataclass
from ..nodes.statement_node import Statement


@dataclass
class WhileStmt(Statement):
    def __init__(self, condition, body):
        self.condition = condition
        self.body = body
