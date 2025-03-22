from dataclasses import dataclass
from ..nodes.statement_node import Statement


@dataclass
class Type(Statement):
    """
    ### 'int' / 'float' / 'char' / 'bool'
    """

    def __init__(self, name):
        self.name = name
