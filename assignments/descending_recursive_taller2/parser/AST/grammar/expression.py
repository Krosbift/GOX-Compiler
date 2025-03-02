from ..node import Node


class Expression(Node):
    """
    ### expression ::= term (('+' | '-') term)*
    """

    def __init__(self, value):
        self.value = value
