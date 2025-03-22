from dataclasses import dataclass
from ..nodes.statement_node import Statement


@dataclass
class VarDecl(Statement):
    """
    ### ('var' / 'const') ID type? ('=' expression)? ';'
    """

    def __init__(self, kind, identifier, var_type, initializer):
        self.type = "VarDecl"
        self.kind = kind
        self.identifier = identifier
        self.var_type = var_type
        self.initializer = initializer
