from dataclasses import dataclass
from ..nodes.statement_node import Statement


@dataclass
class ReturnStmt(Statement):
    """
    ### 'return' expression ';'
    """

    def __init__(self, expression):
        self.type = "ReturnStmt"
        self.expression = expression
