from dataclasses import dataclass
from ..nodes.statement_node import Statement


@dataclass
class IdentifierLocation(Statement):
    def __init__(self, name):
        self.name = name