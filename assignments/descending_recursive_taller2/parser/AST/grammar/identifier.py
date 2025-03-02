from ..node import Node


class Identifier(Node):
    def __init__(self, name):
        self.name = name
