from ..node import Node


class BinaryOperation(Node):
    def __init__(self, left, operator, right):
        self.left = left
        self.operator = operator
        self.right = right
