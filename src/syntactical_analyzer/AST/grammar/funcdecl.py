from dataclasses import dataclass, field
from ..nodes.statement_node import Statement


@dataclass
class Funcdecl(Statement):
    parameters: any
    statements: list[Statement] = field(default_factory=list)
