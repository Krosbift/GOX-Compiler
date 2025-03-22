class LexerError(Exception):
    def __init__(self, errors):
        self.errors = errors
        super().__init__(self._format_errors())

    def _format_errors(self):
        error_messages = []
        error_number = 1
        for token, message in self.errors:
            error_number = error_number + 1
            error_messages.append(f"Error {error_number}: {token} {message}")
        return "\n".join(error_messages)
