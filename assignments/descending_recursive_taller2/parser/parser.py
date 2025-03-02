from .AST.grammar.program import Program
from .AST.grammar.assignment import Assignment
from .AST.grammar.expression import Expression
from .AST.grammar.binary_operation import BinaryOperation
from .AST.grammar.number import Number
from .AST.grammar.identifier import Identifier


class Parser:
    def __init__(self, lexer):
        self.lexer = lexer
        self.current_token = self.lexer.next_token()

    def eat(self, token_type):
        """
        Consume el token actual si coincide con el tipo de token esperado y avanza al siguiente token.

        Args:
            token_type (str): El tipo esperado del token actual.

        Raises:
            SyntaxError: Si el token actual no coincide con el tipo de token esperado.
        """
        if self.current_token[0] == token_type:
            self.current_token = self.lexer.next_token()
        else:
            raise SyntaxError(
                f"Se esperaba {token_type} pero se obtuvo {self.current_token[0]}"
            )

    def parse(self):
        """
        Analiza los tokens de entrada y construye un objeto Program que contiene una lista de declaraciones.

        Este método llama repetidamente a `parse_statement` para analizar declaraciones individuales hasta
        que se encuentra el token de fin de archivo (EOF). Las declaraciones analizadas se recopilan
        en una lista, que luego se usa para crear y devolver un objeto Program.

        Returns:
            Program: Un objeto que representa todo el programa analizado, que contiene una lista de declaraciones.
        """
        statements = []
        while self.current_token[0] != "EOF":
            statements.append(self.parse_statement())
        return Program(statements)

    def parse_statement(self):
        """
        Analiza una declaración en el código fuente.

        Si el token actual es un identificador seguido de un operador de asignación,
        analiza una declaración de asignación. De lo contrario, analiza una declaración de expresión.

        Returns:
            Node: El nodo de la declaración analizada, que puede ser un nodo de asignación
            o un nodo de expresión.
        """
        if self.current_token[0] == "IDENTIFIER" and self.lexer.peek()[0] == "ASSIGN":
            return self.parse_assignment()
        else:
            expr = self.parse_expression()
            self.eat("SEMICOLON")
            return Expression(expr)

    def parse_assignment(self):
        """
        Analiza una declaración de asignación.

        El método espera que el token actual sea un identificador seguido de un
        operador de asignación, una expresión y un punto y coma. Construye y
        devuelve un objeto Assignment.

        Returns:
            Assignment: Un objeto que representa la declaración de asignación.
        """
        identifier = Identifier(self.current_token[1])
        self.eat("IDENTIFIER")
        self.eat("ASSIGN")
        expr = self.parse_expression()
        self.eat("SEMICOLON")
        return Assignment(identifier, expr)

    def parse_expression(self):
        """
        Analiza una expresión de los tokens de entrada.

        Una expresión consiste en uno o más términos separados por operadores PLUS o MINUS.
        Este método analizará el primer término, luego verificará repetidamente si hay operadores PLUS o MINUS,
        y si se encuentran, analizará el término subsiguiente y los combinará en un nodo BinaryOperation.

        Returns:
            Node: El nodo raíz de la expresión analizada, que podría ser un solo término
                  o un nodo BinaryOperation que representa toda la expresión.
        """
        node = self.parse_term()
        while self.current_token[0] in ("PLUS", "MINUS"):
            operator = self.current_token[1]
            self.eat(self.current_token[0])
            node = BinaryOperation(node, operator, self.parse_term())
        return node

    def parse_term(self):
        """
        Analiza un término en la gramática de expresiones.

        Un término se define como un factor posiblemente seguido por cero o más
        operaciones de multiplicación o división.

        Returns:
            Node: El nodo raíz del subárbol del término analizado.
        """
        node = self.parse_factor()
        while self.current_token[0] in ("TIMES", "DIVIDE"):
            operator = self.current_token[1]
            self.eat(self.current_token[0])
            node = BinaryOperation(node, operator, self.parse_factor())
        return node

    def parse_factor(self):
        """
        Analiza un factor en la gramática de expresiones.

        Un factor puede ser uno de los siguientes:
        - Un número (por ejemplo, 42)
        - Un identificador (por ejemplo, nombre de variable)
        - Una expresión entre paréntesis (por ejemplo, (expr))
        - Un menos unario seguido de un factor (por ejemplo, -factor)

        Returns:
            Node: El nodo del factor analizado, que puede ser un Number, Identifier, o un nodo de expresión anidado.

        Raises:
            SyntaxError: Si el token actual no coincide con ninguno de los tipos de factor esperados.
        """
        token = self.current_token
        if token[0] == "NUMBER":
            self.eat("NUMBER")
            return Number(int(token[1]))
        elif token[0] == "IDENTIFIER":
            self.eat("IDENTIFIER")
            return Identifier(token[1])
        elif token[0] == "LPAREN":
            self.eat("LPAREN")
            node = self.parse_expression()
            self.eat("RPAREN")
            return node
        elif token[0] == "MINUS":
            self.eat("MINUS")
            return BinaryOperation(Number(0), "-", self.parse_factor())
        else:
            raise SyntaxError(f"Token inesperado: {token}")
