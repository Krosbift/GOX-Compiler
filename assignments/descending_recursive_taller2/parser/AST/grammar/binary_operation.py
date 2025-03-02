from ..node import Node


class BinaryOperation(Node):
    """
    ### term ::= factor (('*' | '/') factor)*
    """

    def __init__(self, left, operator, right):
        self.left = left
        self.operator = operator
        self.right = right
