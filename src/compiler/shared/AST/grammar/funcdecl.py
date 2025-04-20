from dataclasses import dataclass
from ..nodes.statement_node import Statement


@dataclass
class FuncDecl(Statement):
    """
    ### 'import'? 'func' ID '(' parameters ')' type '{' statement* '}'
    """

    def __init__(self, is_import, identifier, parameters, return_type, body):
        self.is_import = is_import
        self.identifier = identifier
        self.parameters = parameters
        self.return_type = return_type
        self.body = body
