from dataclasses import dataclass
from ..nodes.statement_node import Statement


@dataclass
class IdentifierLocation(Statement):
    """
    ### ID
    """

    def __init__(self, name):
        self.name = name
