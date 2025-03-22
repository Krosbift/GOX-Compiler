from dataclasses import dataclass, field
from ..nodes.statement_node import Statement
from ..types.parameters_types import ParametersType
from ..types.data_types import DataType


@dataclass
class Funcdecl(Statement):
    """
    ### 'import'? 'func' ID '(' parameters ')' type '{' statement* '}'
    """

    def __init__(
        self,
        is_import: bool,
        identifier: str,
        parameters: list[ParametersType],
        return_type: DataType,
        body: list[Statement] = field(default_factory=list),
    ):
        self.is_import: bool = is_import
        self.identifier: str = identifier
        self.parameters: list[ParametersType] = parameters
        self.return_type: DataType = return_type
        self.body: list[Statement] = body
