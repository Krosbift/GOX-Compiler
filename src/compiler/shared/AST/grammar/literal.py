from dataclasses import dataclass
from ..nodes.expression_node import Expression


@dataclass
class Literal(Expression):
    """
    ### INTEGER / FLOAT / CHAR / bool
    """

    def __init__(self, value, type_token):
        self.value = value
        self.type_token = type_token

    def __repr__(self):
        return f"Literal(value={self.value!r}, type_token={self.type_token!r})"
