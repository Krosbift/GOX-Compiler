from ..node import Node


class Expression(Node):
    def __init__(self, value):
        self.value = value
