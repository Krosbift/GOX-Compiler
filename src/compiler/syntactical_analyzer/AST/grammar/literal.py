from dataclasses import dataclass
from ..nodes.statement_node import Statement


@dataclass
class Literal(Statement):
    def __init__(self, value, type_token):
        self.value = value
        self.type_token = type_token