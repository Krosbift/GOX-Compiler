from ..node import Node


class Assignment(Node):
    """
    ### assignment ::= 'ID' '=' expression
    """

    def __init__(self, identifier, expression):
        self.identifier = identifier
        self.expression = expression
