from ..node import Node


class Identifier(Node):
    """
    ### factor ::= 'ID'
    """

    def __init__(self, name):
        self.name = name
