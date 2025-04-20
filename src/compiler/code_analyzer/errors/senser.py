# semantic/errors.py
from colorama import Fore, Style, init

init(autoreset=True)


class SemanticError(Exception):
    """Clase base para errores semánticos."""

    def __init__(self, message, node=None):
        # Intenta obtener info de línea/columna del nodo si existe
        location = ""
        if hasattr(node, "line") and hasattr(
            node, "column"
        ):  # Si los nodos AST tuvieran línea/columna
            location = f" en línea {node.line}, columna {node.column}"
        elif node:
            # Intenta buscar en hijos si el nodo actual no tiene info
            location_info = self._find_location_info(node)
            if location_info:
                location = (
                    f" cerca de línea {location_info[0]}, columna {location_info[1]}"
                )

        super().__init__(
            f"{Fore.RED}Error Semántico{location}:{Style.RESET_ALL} {message}"
        )
        self.node = node

    def _find_location_info(self, node):
        """Intenta encontrar información de ubicación recursivamente en los hijos."""
        if hasattr(node, "line") and hasattr(node, "column"):
            return (node.line, node.column)

        # Busca en atributos comunes que contienen otros nodos o listas de nodos
        possible_children_attrs = [
            "location",
            "expression",
            "condition",
            "initializer",
            "left",
            "right",
            "expr",
            "then_block",
            "else_block",
            "body",
            "statements",
            "args",
            "parameters",
        ]

        for attr_name in possible_children_attrs:
            if hasattr(node, attr_name):
                child_or_list = getattr(node, attr_name)
                if isinstance(child_or_list, list):
                    for item in child_or_list:
                        if hasattr(
                            item, "_find_location_info"
                        ):  # Si es un nodo AST nuestro
                            loc = self._find_location_info(item)
                            if loc:
                                return loc
                        elif (
                            isinstance(item, tuple)
                            and len(item) > 0
                            and hasattr(item[0], "_find_location_info")
                        ):  # e.g., parameters
                            loc = self._find_location_info(item[0])
                            if loc:
                                return loc
                elif hasattr(
                    child_or_list, "_find_location_info"
                ):  # Si es un solo nodo
                    loc = self._find_location_info(child_or_list)
                    if loc:
                        return loc
        return None  # No se encontró


class TypeMismatchError(SemanticError):
    pass


class UndeclaredIdentifierError(SemanticError):
    pass


class RedeclarationError(SemanticError):
    pass


class AssignmentError(SemanticError):
    pass


class FunctionError(SemanticError):
    pass


class ScopeError(SemanticError):
    pass
