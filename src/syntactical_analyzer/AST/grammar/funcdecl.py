from dataclasses import dataclass, field
from ..nodes.statement_node import Statement
from ..types.parameters_types import ParametersType
from ..types.data_types import DataType


@dataclass
class Funcdecl(Statement):
    """
    ### 'import'? 'func' ID '(' parameters ')' type '{' statement* '}'
    """

    identifier: str
    parameters: list[ParametersType]
    type: DataType
    statements: list[Statement] = field(default_factory=list)
