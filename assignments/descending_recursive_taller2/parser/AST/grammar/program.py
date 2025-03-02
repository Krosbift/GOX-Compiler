from ..node import Node


class Program(Node):
    def __init__(self, statements):
        self.statements = statements
