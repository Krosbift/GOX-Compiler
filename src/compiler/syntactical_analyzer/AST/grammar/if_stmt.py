from dataclasses import dataclass
from ..nodes.statement_node import Statement


@dataclass
class IfStmt(Statement):
    """
    ### 'if' expression '{' statement* '}' ('else' '{' statement* '}')?
    """

    def __init__(self, condition, then_block, else_block):
        self.type = "IfStmt"
        self.condition = condition
        self.then_block = then_block
        self.else_block = else_block
