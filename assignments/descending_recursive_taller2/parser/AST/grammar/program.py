from ..node import Node


class Program(Node):
    """
    ### program ::= statement*
    """

    def __init__(self, statements):
        self.statements = statements
