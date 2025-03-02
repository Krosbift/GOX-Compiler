from dataclasses import dataclass
from ..node import Node

@dataclass
class Statement(Node):
    """
    ### statement <- assignment
    ###       / vardecl
    ###       / funcdecl
    ###       / if_stmt
    ###       / while_stmt
    ###       / break_stmt
    ###       / continue_stmt
    ###       / return_stmt
    ###       / print_stmt
    """
    pass
