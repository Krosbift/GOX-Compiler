from ..node import Node


class Number(Node):
    """
    ### factor ::= 'NUMBER'
    """

    def __init__(self, value):
        self.value = value
