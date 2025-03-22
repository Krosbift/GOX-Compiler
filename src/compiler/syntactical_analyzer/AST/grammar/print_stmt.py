from dataclasses import dataclass
from ..nodes.statement_node import Statement


@dataclass
class PrintStmt(Statement):
    """
    ### 'print' expression ';'
    """

    def __init__(self, expression):
        self.type = "PrintStmt"
        self.expression = expression
