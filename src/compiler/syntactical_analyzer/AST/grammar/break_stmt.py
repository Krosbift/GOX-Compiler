from dataclasses import dataclass
from ..nodes.statement_node import Statement


@dataclass
class BreakStmt(Statement):
    """
    ### 'break' ';'
    """

    def __init__(self):
        self.type = "BreakStmt"
