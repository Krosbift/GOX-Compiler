from dataclasses import dataclass
from ..types.data_types import DataType
from ..nodes.statement_node import Statement
from ..nodes.expression_node import Expression
from ..types.declaration_types import DeclarationType


@dataclass
class Vardecl(Statement):
    """
    ### ('var' / 'const') ID type? ('=' expression)? ';'
    """

    def __init__(
        self,
        kind: DeclarationType,
        identifier: str,
        var_type: DataType,
        initializer: Expression,
    ):
        self.kind: DeclarationType = kind
        self.identifier: str = identifier
        self.var_type: DataType = var_type
        self.initializer: Expression = initializer
