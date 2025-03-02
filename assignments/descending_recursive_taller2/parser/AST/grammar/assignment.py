from ..node import Node


class Assignment(Node):
    def __init__(self, identifier, expression):
        self.identifier = identifier
        self.expression = expression
