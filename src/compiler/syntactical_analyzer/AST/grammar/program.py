from dataclasses import dataclass
from ..node import Node


@dataclass
class Program(Node):
    """
    ### statement* EOF
    """

    def __init__(self, statements):
        self.statements = statements
