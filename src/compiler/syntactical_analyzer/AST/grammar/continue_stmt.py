from dataclasses import dataclass
from ..nodes.statement_node import Statement


@dataclass
class ContinueStmt(Statement):
    """
    ### 'continue' ';'
    """
