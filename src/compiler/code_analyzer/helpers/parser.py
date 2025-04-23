from ...shared.grammar.gox_token import Token


class ParserHelper:
    @staticmethod
    def peek_token(parser):
        if parser.tokens:
            return parser.tokens[0]
        else:
            return None

    @staticmethod
    def expect(parser, token_type):
        if parser.current_token and parser.current_token.type == token_type:
            value = parser.current_token.value
            parser.next_token()
            return value
        else:
            ParserHelper.error(
                parser,
                f"Se esperaba el token {token_type}, pero se obtuvo {parser.current_token}",
            )

    @staticmethod
    def expect_type(parser):
        if parser.current_token and parser.current_token.type in (
            "INT",
            "FLOAT_TYPE",
            "CHAR_TYPE",
            "BOOL",
        ):
            value = parser.current_token.value
            parser.next_token()
            return value
        else:
            ParserHelper.error(
                parser,
                f"Se esperaba un token TYPE, pero se obtuvo {parser.current_token}",
            )

    @staticmethod
    def error(parser, message):
        token_type, value, line_number, column_number = (
            parser.current_token if parser.current_token else (None, None, None, None)
        )
        parser.errors.append(
            (Token(token_type, value, line_number, column_number), message)
        )
        parser.next_token()
