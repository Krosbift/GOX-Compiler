class Helper:
    @staticmethod
    def expect(parser, token_type):
        if parser.current_token.type == token_type:
            value = parser.current_token.value
            parser.next_token()
            return value
        else:
            Helper.error(f"Expected token {token_type}, but got {parser.current_token}")

    @staticmethod
    def error(message):
        raise SyntaxError(message)

    @staticmethod
    def peek_token(parser):
        if parser.tokens:
            return parser.tokens[0]
        else:
            return None

    @staticmethod
    def expect_type(parser):
        if parser.current_token.type in ("INT", "FLOAT_TYPE", "CHAR_TYPE", "BOOL"):
            value = parser.current_token.value
            parser.next_token()
            return value
        else:
            Helper.error(f"Expected type token, but got {parser.current_token}")
