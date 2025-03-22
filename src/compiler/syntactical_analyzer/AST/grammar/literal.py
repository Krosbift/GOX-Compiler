from dataclasses import dataclass
from ..nodes.statement_node import Statement


@dataclass
class Literal(Statement):
    """
    ### INTEGER / FLOAT / CHAR / bool
    """

    def __init__(self, value, type_token):
        self.type = "Literal"
        self.value = value
        self.type_token = type_token
