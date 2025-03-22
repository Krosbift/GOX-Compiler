from dataclasses import dataclass
from ..nodes.statement_node import Statement


@dataclass
class DereferenceLocation(Statement):
    def __init__(self, expression):
        self.expression = expression
