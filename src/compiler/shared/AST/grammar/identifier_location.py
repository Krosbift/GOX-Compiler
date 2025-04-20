from dataclasses import dataclass
from ..nodes.expression_node import Expression


@dataclass
class IdentifierLocation(Expression):
    """
    ### ID
    """

    def __init__(self, name):
        self.name = name
