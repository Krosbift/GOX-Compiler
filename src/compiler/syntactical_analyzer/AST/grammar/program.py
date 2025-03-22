from dataclasses import dataclass, field
from ..node import Node
from ..nodes.statement_node import Statement


@dataclass
class Program(Node):
    """
    ### statement* EOF
    """

    statements: list[Statement] = field(default_factory=list)
