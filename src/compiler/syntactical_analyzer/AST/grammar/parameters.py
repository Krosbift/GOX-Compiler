from dataclasses import dataclass
from ..nodes.statement_node import Statement


@dataclass
class Parameters(Statement):
    def __init__(self, params):
        self.params = params
