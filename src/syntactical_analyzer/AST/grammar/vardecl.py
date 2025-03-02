from dataclasses import dataclass
from ..nodes.statement_node import Statement
from ..nodes.expression_node import Expression


@dataclass
class Vardecl(Statement):
    """
    ### ('var' / 'const') ID type? ('=' expression)? ';'
    """

    kind: DeclarationType
    identifier: str
    type: DataType
    initializer: Expression
