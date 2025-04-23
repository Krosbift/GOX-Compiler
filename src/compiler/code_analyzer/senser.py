import traceback

# --- Import Error Type (if using a specific one) ---
from .errors.senser import (
    SemanticError,
    TypeMismatchError,
    UndeclaredIdentifierError,
    RedeclarationError,
    AssignmentError,
    FunctionError,
    ScopeError,
    # Define or import MissingReturnError if desired
)

# --- End Import Error Type ---

from ..shared.table.symbol_table import (
    SymbolTable,
    Symbol,
    Scope,
)
from ..shared.table.types import (
    TYPE_INT,
    TYPE_FLOAT,
    TYPE_BOOL,
    TYPE_CHAR,
    TYPE_VOID,
    TYPE_ERROR,
    get_type_from_name,
    is_numeric,
    is_boolean,
    is_compatible_for_assignment,
    check_binary_op_type,
    check_unary_op_type,
)

# ... rest of imports remain the same ...
from ..shared.AST.grammar.program import Program
from ..shared.AST.grammar.assigment import Assignment
from ..shared.AST.grammar.vardecl import VarDecl
from ..shared.AST.grammar.funcdecl import FuncDecl
from ..shared.AST.grammar.if_stmt import IfStmt
from ..shared.AST.grammar.while_stmt import WhileStmt
from ..shared.AST.grammar.break_stmt import BreakStmt
from ..shared.AST.grammar.continue_stmt import ContinueStmt
from ..shared.AST.grammar.return_stmt import ReturnStmt
from ..shared.AST.grammar.print_stmt import PrintStmt
from ..shared.AST.grammar.parameters import Parameters
from ..shared.AST.grammar.binary_operator import BinaryOp
from ..shared.AST.grammar.unary_operator import UnaryOp
from ..shared.AST.grammar.literal import Literal
from ..shared.AST.grammar.identifier_location import IdentifierLocation
from ..shared.AST.grammar.dereference_location import DereferenceLocation
from ..shared.AST.grammar.function_call import FunctionCall
from ..shared.AST.grammar.cast import Cast


# --- Optional: Define MissingReturnError ---
class MissingReturnError(FunctionError):
    """Indicates that a non-void function lacks a return statement on some/all paths."""

    pass


# --- End Optional ---


class Senser:
    def __init__(self):
        self.symbol_table = SymbolTable()
        self.errors = []
        self.current_function_return_type = None
        # --- Add Flag for Return Check ---
        self.current_function_found_return = (
            False  # Tracks if return was seen in current function
        )
        # --- End Add Flag ---
        self.loop_level = 0
        self.ast_root = None

    def add_error(self, error: SemanticError):
        self.errors.append(error)

    def visit(self, node):
        method_name = f"visit_{type(node).__name__}"
        visitor = getattr(self, method_name, self.generic_visit)
        # try: # Optional: Add try-except around visitor calls for finer-grained error node reporting
        return visitor(node)
        # except SemanticError as e:
        #     self.add_error(e)
        #     return TYPE_ERROR # Propagate error type
        # except Exception as e:
        #      # Try to associate internal errors with the current node being visited
        #      node_info = node if hasattr(node, 'line') else getattr(node, 'token', None)
        #      self.add_error(SemanticError(f"Internal Senser Error visiting {type(node).__name__}: {e}", node_info))
        #      traceback.print_exc()
        #      return TYPE_ERROR

    def generic_visit(self, node):
        # print(f"Warning: No specific visitor for {type(node).__name__}")
        return None

    def analyze(self, ast_root: Program):
        self.ast_root = ast_root
        self.errors = []
        self.symbol_table = SymbolTable()
        self.current_function_return_type = None
        # --- Reset Flag ---
        self.current_function_found_return = False
        # --- End Reset Flag ---
        self.loop_level = 0

        try:
            self.visit(ast_root)
        except (
            SemanticError
        ) as e:  # Catch errors potentially raised directly by visitors
            self.add_error(e)
        except Exception as e:  # Catch unexpected errors
            self.add_error(
                SemanticError(
                    f"Error interno irrecuperable del Senser: {e}",
                    self.ast_root,  # Associate with root if node unknown
                )
            )
            traceback.print_exc()

        # --- Main Function Check ---
        # Ensure symbol table was initialized before checking
        if self.symbol_table.scope_stack:
            self._check_for_main_function()
        else:
            # This might happen if an exception occurred very early
            self.add_error(
                SemanticError(
                    "Tabla de símbolos no inicializada, no se pudo verificar 'main'.",
                    self.ast_root,
                )
            )
        # --- End Main Function Check ---

        if self.errors:
            print(f"{len(self.errors)} Errores Semánticos Encontrados:")
            # Sort errors by line number if possible for better readability
            self.errors.sort(
                key=lambda e: getattr(getattr(e, "node", None), "line", float("inf"))
            )
            for error in self.errors:
                loc_info = ""
                node_for_loc = getattr(error, "node", None)
                if node_for_loc:
                    line = getattr(node_for_loc, "line", None)
                    col = getattr(node_for_loc, "column", None)
                    # Fallback to token if node doesn't have line/col directly
                    if (
                        line is None
                        and hasattr(node_for_loc, "token")
                        and node_for_loc.token
                    ):
                        line = getattr(node_for_loc.token, "line", None)
                        col = getattr(node_for_loc.token, "column", None)
                    if line is not None:
                        loc_info = (
                            f" (Linea: {line}"
                            + (f", Columna: {col}" if col is not None else "")
                            + ")"
                        )

                print(f"- {error}{loc_info}")
            # Print symbol table even with errors for debugging
            print("\nTabla de Símbolos (puede ser inválida debido a errores):")
            self.symbol_table.print_table()
            return None

        else:
            print("No se encontraron errores semánticos.")
            print("\nTabla de Símbolos Final:")
            self.symbol_table.print_table()
            return self.symbol_table

    def _check_for_main_function(self):
        # Ensure scope stack is not empty
        if not self.symbol_table.scope_stack:
            self.add_error(
                SemanticError(
                    "Error interno: Stack de scopes vacío al verificar 'main'.",
                    self.ast_root,
                )
            )
            return

        global_scope = self.symbol_table.scope_stack[0]
        main_symbol = global_scope.symbols.get("main")

        if main_symbol is None:
            self.add_error(
                FunctionError(
                    "No se encontró la función 'main' definida en el scope global. Se requiere una función 'main' como punto de entrada.",
                    self.ast_root,
                )
            )
        elif main_symbol.kind != "func":
            self.add_error(
                FunctionError(
                    f"El identificador 'main' en el scope global debe ser una función, pero se encontró un '{main_symbol.kind}'.",
                    main_symbol.node,
                )
            )
        # Optional: Add checks for main's signature if needed
        # elif main_symbol.type[2] != TYPE_VOID: # Example: main must return void
        #     self.add_error(FunctionError("La función 'main' debe tener tipo de retorno VOID.", main_symbol.node))
        # elif main_symbol.type[1]: # Example: main must take no parameters
        #     self.add_error(FunctionError("La función 'main' no debe aceptar parámetros.", main_symbol.node))

    # --- Visitors ---

    def visit_Program(self, node: Program):
        for statement in node.statements:
            self.visit(statement)

    def visit_VarDecl(self, node: VarDecl):
        var_name = node.identifier
        declared_type_name = node.var_type  # Can be None
        declared_type = (
            get_type_from_name(declared_type_name) if declared_type_name else None
        )
        is_const = node.kind == "CONST"
        initializer_value = None  # Store the actual value node for error reporting
        initializer_type = None

        # Check for redeclaration in the *current* scope
        existing_symbol = self.symbol_table.resolve_current_scope(var_name)
        if existing_symbol:
            self.add_error(
                RedeclarationError(
                    f"Identificador '{var_name}' ya declarado en este scope (como '{existing_symbol.kind}' en la linea {getattr(existing_symbol.node, 'line', '?')}).",
                    node,
                )
            )
            # Still define an error symbol to potentially prevent cascade errors, but don't process further.
            error_symbol = Symbol(
                var_name,
                "var",
                TYPE_ERROR,
                self.symbol_table.current_scope.level,
                False,
                False,
                node,
            )
            self.symbol_table.define(error_symbol)
            return

        effective_type = declared_type

        # Process initializer
        if node.initializer:
            initializer_value = node.initializer
            initializer_type = self.visit(initializer_value)
            if initializer_type == TYPE_ERROR:
                effective_type = TYPE_ERROR  # Propagate error
            elif declared_type:
                # Type declared AND initializer: check compatibility
                if not is_compatible_for_assignment(declared_type, initializer_type):
                    self.add_error(
                        TypeMismatchError(
                            f"No se puede inicializar la variable '{var_name}' (tipo '{declared_type}') con un valor de tipo '{initializer_type}'.",
                            initializer_value,  # Point to the initializer expression
                        )
                    )
                    effective_type = TYPE_ERROR
                # If compatible, effective_type remains declared_type
            else:
                # No type declared, infer from initializer
                if (
                    initializer_type == TYPE_VOID
                ):  # Cannot infer variable type from void
                    self.add_error(
                        SemanticError(
                            f"No se puede declarar la variable '{var_name}' con un inicializador de tipo '{TYPE_VOID}'.",
                            initializer_value,
                        )
                    )
                    effective_type = TYPE_ERROR
                else:
                    effective_type = initializer_type  # Infer the type
        elif not declared_type:
            # No type and no initializer -> Error
            self.add_error(
                SemanticError(
                    f"La declaración de variable '{var_name}' debe tener un tipo explícito o un valor inicializador.",
                    node,
                )
            )
            effective_type = TYPE_ERROR
        elif is_const:
            # Const without initializer -> Error
            self.add_error(
                AssignmentError(
                    f"La constante '{var_name}' debe ser inicializada en su declaración.",
                    node,
                )
            )
            # Keep declared type if valid, but mark as error overall? Or set effective_type = TYPE_ERROR?
            # Let's set to error type to be clear it's an invalid state.
            effective_type = TYPE_ERROR

        # If effective_type is still None (shouldn't happen with above logic) or became error
        if effective_type is None or effective_type == TYPE_ERROR:
            final_type = TYPE_ERROR
            initialized_state = False
        else:
            final_type = effective_type
            initialized_state = bool(
                node.initializer
            )  # Mark initialized if initializer was present and valid type

        # Define the symbol (only if no redeclaration error occurred earlier)
        symbol = Symbol(
            name=var_name,
            kind="const" if is_const else "var",
            type=final_type,
            # scope_level is handled by symbol_table.define
            is_mutable=not is_const,
            initialized=initialized_state,
            node=node,
        )
        self.symbol_table.define(symbol)

    def visit_Assignment(self, node: Assignment):
        location_node = node.location
        location_type = self.visit(
            location_node
        )  # This should handle UndeclaredIdentifierError for location

        if location_type == TYPE_ERROR:
            return  # Error already reported by location visitor

        # Check if the location represents an l-value (assignable)
        symbol = None
        is_assignable = False
        if isinstance(location_node, IdentifierLocation):
            symbol = self.symbol_table.resolve(location_node.name)
            if symbol:  # Should exist if visit_IdentifierLocation didn't return error
                if symbol.kind == "var" or symbol.kind == "param":
                    # Variables and parameters are generally mutable
                    is_assignable = True
                elif symbol.kind == "const":
                    self.add_error(
                        AssignmentError(
                            f"No se puede asignar a la constante '{symbol.name}'.", node
                        )
                    )
                else:  # e.g., assigning to a function name
                    self.add_error(
                        AssignmentError(
                            f"No se puede asignar al identificador '{symbol.name}' (es de tipo '{symbol.kind}').",
                            node,
                        )
                    )
            # else case handled by visit_IdentifierLocation reporting undeclared
        elif isinstance(location_node, DereferenceLocation):
            # Placeholder: Assume dereference yields an l-value if implemented
            is_assignable = True  # Needs real pointer semantics check
        else:
            # Should not happen with valid AST nodes for location
            self.add_error(
                AssignmentError(
                    "La parte izquierda de la asignación no es una location válida.",
                    node,
                )
            )

        # Visit the right-hand side expression
        expr_node = node.expression
        expr_type = self.visit(expr_node)

        if expr_type == TYPE_ERROR:
            return  # Error reported by expression visitor

        # If location is assignable and no previous errors, check type compatibility
        if is_assignable:
            if not is_compatible_for_assignment(location_type, expr_type):
                loc_name = getattr(
                    location_node, "name", "location"
                )  # Get name if IdentifierLocation
                self.add_error(
                    TypeMismatchError(
                        f"No se puede asignar un valor de tipo '{expr_type}' a '{loc_name}' que tiene tipo '{location_type}'.",
                        expr_node,  # Point error to the expression providing the wrong type
                    )
                )
            elif symbol:  # If direct assignment to var/param, mark initialized
                symbol.initialized = True

    def visit_IdentifierLocation(self, node: IdentifierLocation):
        name = node.name
        symbol = self.symbol_table.resolve(name)
        if not symbol:
            self.add_error(
                UndeclaredIdentifierError(f"Identificador '{name}' no declarado.", node)
            )
            node.type = TYPE_ERROR
            return TYPE_ERROR
        elif symbol.kind == "func":
            # Allow using func name if context expects a function (e.g., function pointers),
            # but usually not as a variable location.
            self.add_error(
                SemanticError(
                    f"No se puede usar el nombre de la función '{name}' en este contexto (como variable/location).",
                    node,
                )
            )
            node.type = TYPE_ERROR  # Or a specific function type if needed later
            return TYPE_ERROR
        # Add check for using uninitialized variables if required by language rules
        # elif symbol.kind in ('var', 'const') and not symbol.initialized and not context_is_assignment_lhs:
        #     self.add_error(SemanticError(f"Variable '{name}' usada antes de ser inicializada.", node))
        #     # Might return symbol.type or TYPE_ERROR depending on how strict
        node.type = symbol.type
        return symbol.type

    # ... (visit_DereferenceLocation, visit_Literal, visit_BinaryOp, visit_UnaryOp, visit_Cast remain largely the same) ...

    def visit_FuncDecl(self, node: FuncDecl):
        func_name = node.identifier
        # --- Handle default return type correctly ---
        return_type_name = (
            node.return_type if node.return_type else "VOID"
        )  # Default to VOID string
        return_type = get_type_from_name(return_type_name)
        # --- End Handle default return type ---

        if (
            return_type is None
        ):  # Should only happen if get_type_from_name fails for a non-None name
            self.add_error(
                SemanticError(
                    f"Tipo de retorno desconocido '{return_type_name}' para la función '{func_name}'.",
                    node,  # Point to the whole declaration
                )
            )
            return_type = TYPE_ERROR  # Use error type moving forward

        # --- Pre-process Parameters ---
        param_types = []
        param_names = set()
        has_param_errors = False
        processed_params = []
        if node.parameters and node.parameters.params:
            # Assuming node.parameters.params is iterable of (name_token, type_token) or similar
            for (
                p_name_token,
                p_type_token,
            ) in node.parameters.params:  # Adjust based on actual AST structure
                p_name = getattr(
                    p_name_token, "value", str(p_name_token)
                )  # Get name string
                p_type_name = getattr(
                    p_type_token, "value", str(p_type_token)
                )  # Get type name string
                param_type = get_type_from_name(p_type_name)
                param_node_ref = p_name_token  # Use token/node for error reporting

                if param_type is None:
                    self.add_error(
                        SemanticError(
                            f"Tipo de parámetro desconocido '{p_type_name}' para '{p_name}' en la función '{func_name}'.",
                            param_node_ref,
                        )
                    )
                    param_type = TYPE_ERROR
                    has_param_errors = True

                if p_name in param_names:
                    self.add_error(
                        RedeclarationError(
                            f"Nombre de parámetro duplicado '{p_name}' en la declaración de la función '{func_name}'.",
                            param_node_ref,
                        )
                    )
                    has_param_errors = True
                else:
                    param_names.add(p_name)

                param_types.append(param_type)
                processed_params.append(
                    (p_name, param_type, param_node_ref)
                )  # Store node ref too

        func_type_signature = ("func", tuple(param_types), return_type)

        # --- Define Function Symbol ---
        existing_symbol = self.symbol_table.resolve_current_scope(func_name)
        if existing_symbol:
            self.add_error(
                RedeclarationError(
                    f"Redeclaración del identificador '{func_name}'. Ya existe como '{existing_symbol.kind}' en este scope (linea {getattr(existing_symbol.node, 'line', '?')}).",
                    node,
                )
            )
            return  # Don't proceed if name is already taken in this scope

        func_symbol = Symbol(
            name=func_name,
            kind="func",
            type=func_type_signature,
            scope_level=self.symbol_table.current_scope.level,
            is_mutable=False,
            initialized=True,  # Function is defined by its declaration
            node=node,
        )
        self.symbol_table.define(func_symbol)

        # If parameter definition had errors, don't analyze body
        if has_param_errors:
            return

        self.symbol_table.enter_scope()

        # --- Manage Function Context for Return Check ---
        previous_function_return_type = self.current_function_return_type
        previous_found_return = (
            self.current_function_found_return
        )  # Save outer function's state
        self.current_function_return_type = return_type
        self.current_function_found_return = False  # Reset for *this* function
        # --- End Manage Function Context ---

        # Define parameter symbols in the new scope
        if processed_params:
            param_name_check = set()  # Track names defined in *this* scope
            for p_name, param_type, param_node_ref in processed_params:
                if p_name not in param_name_check:  # Avoid defining duplicates again
                    param_symbol = Symbol(
                        name=p_name,
                        kind="param",
                        type=param_type,
                        # scope_level handled by define
                        is_mutable=True,  # Params are usually mutable locally
                        initialized=True,  # Params are initialized by arguments at call time
                        node=param_node_ref,  # Point symbol to param declaration
                    )
                    self.symbol_table.define(param_symbol)
                    param_name_check.add(p_name)

        # Visit the function body statements
        # Use a flag to track if body processing was cut short by an error inside
        body_processed_fully = True
        try:
            for statement in node.body:
                self.visit(statement)
        except SemanticError as e:  # Catch error during body processing
            self.add_error(e)
            body_processed_fully = False
        except Exception as e:
            self.add_error(
                SemanticError(
                    f"Internal error processing body of '{func_name}': {e}", node
                )
            )
            traceback.print_exc()
            body_processed_fully = False

        # --- Check for Missing Return AFTER Visiting Body ---
        # Only perform this check if the body was processed without fatal errors inside
        # and the function is expected to return a value.
        if (
            body_processed_fully
            and return_type != TYPE_VOID
            and return_type != TYPE_ERROR
        ):
            if not self.current_function_found_return:
                # Report error: non-void function has no return statement encountered
                self.add_error(
                    MissingReturnError(  # Use specific error class
                        f"La función '{func_name}' debe retornar un valor de tipo '{return_type}', pero no se encontró una declaración 'return' (o no todas las rutas de código retornan).",
                        node,  # Associate error with the function declaration node
                    )
                )
        # --- End Check for Missing Return ---

        # --- Exit Function Scope & Restore State ---
        self.symbol_table.exit_scope()
        self.current_function_return_type = previous_function_return_type
        self.current_function_found_return = (
            previous_found_return  # Restore outer function's state
        )
        # --- End Exit Function Scope ---

    def visit_FunctionCall(self, node: FunctionCall):
        func_name = node.name
        func_symbol = self.symbol_table.resolve(func_name)

        if not func_symbol:
            self.add_error(
                UndeclaredIdentifierError(
                    f"Llamada a función no declarada '{func_name}'.", node
                )
            )
            node.type = TYPE_ERROR
            return TYPE_ERROR
        elif func_symbol.kind != "func":
            self.add_error(
                SemanticError(
                    f"'{func_name}' no es una función (es '{func_symbol.kind}'), no se puede llamar.",
                    node,
                )
            )
            node.type = TYPE_ERROR
            return TYPE_ERROR

        # Extract signature details from the symbol's type
        # Assuming type is stored as ('func', (param_types...), return_type)
        try:
            func_sig_tuple = func_symbol.type
            expected_param_types = func_sig_tuple[1]
            expected_return_type = func_sig_tuple[2]
            expected_param_count = len(expected_param_types)
        except (TypeError, IndexError):
            self.add_error(
                SemanticError(
                    f"Error interno: Formato de signatura inválido para función '{func_name}'.",
                    func_symbol.node,
                )
            )
            node.type = TYPE_ERROR
            return TYPE_ERROR

        actual_arg_count = len(node.arguments)

        # Check argument count
        if expected_param_count != actual_arg_count:
            self.add_error(
                FunctionError(
                    f"La función '{func_name}' esperaba {expected_param_count} argumento(s), pero se pasaron {actual_arg_count}.",
                    node,  # Error on the call itself
                )
            )
            node.type = TYPE_ERROR
            return TYPE_ERROR  # Stop if arg count mismatch

        # Check argument types
        types_ok = True
        for i, arg_expr in enumerate(node.arguments):
            arg_type = self.visit(arg_expr)
            if arg_type == TYPE_ERROR:
                types_ok = False  # Error already reported by arg visitor
                continue

            expected_param_type = expected_param_types[i]

            # Check compatibility (e.g., allow INT arg for FLOAT param, but not vice-versa without cast)
            if not is_compatible_for_assignment(expected_param_type, arg_type):
                self.add_error(
                    TypeMismatchError(
                        f"Argumento {i+1} inválido para '{func_name}'. Se esperaba tipo compatible con '{expected_param_type}', pero se pasó tipo '{arg_type}'.",
                        arg_expr,  # Point error to the specific argument
                    )
                )
                types_ok = False

        if not types_ok:
            node.type = TYPE_ERROR
            return TYPE_ERROR

        # If all checks pass, the type of the call is the function's return type
        node.type = expected_return_type
        return expected_return_type

    def visit_ReturnStmt(self, node: ReturnStmt):
        # --- Set Flag Indicating Return was Found ---
        if self.current_function_return_type is not None:
            # Only set the flag if we are semantically inside a function
            self.current_function_found_return = True
        # --- End Set Flag ---
        else:
            # This return is outside any function scope
            self.add_error(
                ScopeError(
                    "Declaración 'return' inválida: no está dentro de una función.",
                    node,
                )
            )
            return  # Don't perform type checks if scope is wrong

        # Now, check types based on the function context established by visit_FuncDecl
        expected_return_type = self.current_function_return_type

        # Case 1: Return in a VOID function
        if expected_return_type == TYPE_VOID:
            if node.expression:
                # If there's an expression, visit it to find errors within, but its value is disallowed
                actual_return_type = self.visit(node.expression)
                # Only report the error if the expression itself was valid (not TYPE_ERROR)
                # because returning an erroneous expression from void is doubly wrong, but the primary issue is returning *anything*.
                if actual_return_type != TYPE_ERROR:
                    self.add_error(
                        FunctionError(
                            f"Una función con tipo de retorno '{TYPE_VOID}' no debe retornar un valor (se encontró expresión de tipo '{actual_return_type}').",
                            node.expression,  # Point to the problematic expression
                        )
                    )
            # else: `return;` (no expression) in a void function is correct.

        # Case 2: Return in a NON-VOID function
        else:
            if not node.expression:
                # Non-void function requires a return value
                self.add_error(
                    FunctionError(
                        f"Declaración 'return' en función con tipo de retorno '{expected_return_type}' debe especificar un valor.",
                        node,  # Error on the return statement itself
                    )
                )
                return  # Stop processing this return if no value provided

            # Visit the expression to get its type
            actual_return_type = self.visit(node.expression)

            if actual_return_type == TYPE_ERROR:
                return  # Error already reported by expression visitor

            # Check if the actual returned type is compatible with the expected type
            if not is_compatible_for_assignment(
                expected_return_type, actual_return_type
            ):
                self.add_error(
                    TypeMismatchError(
                        f"Tipo de retorno inválido. La función esperaba retornar '{expected_return_type}', pero se retorna un valor de tipo '{actual_return_type}'.",
                        node.expression,  # Point error to the expression being returned
                    )
                )
            # else: Types are compatible, return is valid.

    def visit_IfStmt(self, node: IfStmt):
        condition_node = node.condition
        condition_type = self.visit(condition_node)

        if condition_type != TYPE_ERROR and not is_boolean(condition_type):
            self.add_error(
                TypeMismatchError(
                    f"La condición del 'if' debe ser de tipo '{TYPE_BOOL}', pero se encontró tipo '{condition_type}'.",
                    condition_node,
                )
            )

        # Visit 'then' block in a new scope
        self.symbol_table.enter_scope("If-Then Block")
        try:
            for statement in node.then_block:
                self.visit(statement)
        finally:  # Ensure scope exit even if error occurs inside
            self.symbol_table.exit_scope()

        # Visit 'else' block (if present) in its own new scope
        if node.else_block:
            self.symbol_table.enter_scope("If-Else Block")
            try:
                for statement in node.else_block:
                    self.visit(statement)
            finally:  # Ensure scope exit
                self.symbol_table.exit_scope()

    def visit_WhileStmt(self, node: WhileStmt):
        condition_node = node.condition
        condition_type = self.visit(condition_node)

        if condition_type != TYPE_ERROR and not is_boolean(condition_type):
            self.add_error(
                TypeMismatchError(
                    f"La condición del 'while' debe ser de tipo '{TYPE_BOOL}', pero se encontró tipo '{condition_type}'.",
                    condition_node,
                )
            )

        # Enter loop context and new scope
        self.loop_level += 1
        self.symbol_table.enter_scope("While Loop Body")
        try:
            # Visit the loop body
            for statement in node.body:
                self.visit(statement)
        finally:  # Ensure scope exit and loop level decrement even if error occurs inside
            self.symbol_table.exit_scope()
            self.loop_level -= 1

    def visit_BreakStmt(self, node: BreakStmt):
        if self.loop_level <= 0:
            self.add_error(
                ScopeError(
                    "Declaración 'break' inválida: no está dentro de un bucle ('while').",
                    node,
                )
            )

    def visit_ContinueStmt(self, node: ContinueStmt):
        if self.loop_level <= 0:
            self.add_error(
                ScopeError(
                    "Declaración 'continue' inválida: no está dentro de un bucle ('while').",
                    node,
                )
            )

    def visit_PrintStmt(self, node: PrintStmt):
        expression_node = node.expression
        expr_type = self.visit(expression_node)

        if expr_type == TYPE_ERROR:
            pass  # Error already reported
        elif expr_type == TYPE_VOID:
            self.add_error(
                TypeMismatchError(
                    f"La declaración 'print' no puede imprimir un valor de tipo '{TYPE_VOID}'.",
                    expression_node,
                )
            )
        # You could add more checks here, e.g., disallowing printing of complex types like functions if applicable

    def visit_Parameters(self, node: Parameters):
        # Parameter processing is handled within visit_FuncDecl
        pass
