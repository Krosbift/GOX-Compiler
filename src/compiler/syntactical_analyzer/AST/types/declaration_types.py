from enum import Enum


class DeclarationType(Enum):
    """
    ### vardecl -> 'var' / 'const'
    """

    VAR = "var"
    CONST = "const"
