from dataclasses import dataclass

from src.syntactical_analyzer.AST.types.data_types import DataType
from ..nodes.statement_node import Statement
from ..nodes.expression_node import Expression
from ..types.declaration_types import DeclarationType


@dataclass
class Vardecl(Statement):
    """
    ### ('var' / 'const') ID type? ('=' expression)? ';'
    """

    kind: DeclarationType
    identifier: str
    type: DataType
    initializer: Expression

