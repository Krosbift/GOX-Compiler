from dataclasses import dataclass
from ..nodes.statement_node import Statement


@dataclass
class Parameters(Statement):
    """
    ### ID type (',' ID type)* / empty
    """

    def __init__(self, params):
        self.type = "Parameters"
        self.params = params
