from enum import Enum, auto


class SymbolKind(Enum):
    VARIABLE = auto()
    CONSTANT = auto()
    FUNCTION = auto()
    PARAMETER = auto()


class Symbol:
    def __init__(
        self,
        name,
        kind,
        sym_type,
        node=None,
        params_info=None,
        return_type=None,
        is_import=False,
    ):
        self.name = name
        self.kind = kind
        self.type = sym_type
        self.node = node
        self.initialized = (kind == SymbolKind.PARAMETER) or (
            kind == SymbolKind.FUNCTION
        )
        self.params_info = params_info if params_info is not None else []
        self.return_type = return_type
        self.is_import = is_import
        self.has_return_statement = False

    def __str__(self):
        if self.kind == SymbolKind.FUNCTION:
            param_types_str = ", ".join([p_type for _, p_type, _ in self.params_info])
            return f"Symbol({self.name}, FUNCTION, ({param_types_str}) -> {self.return_type or 'void'})"
        return f"Symbol({self.name}, {self.kind}, {self.type})"
