class Token:
    def __init__(self, type, value, line, column):
        self.type = type
        self.value = value
        self.line = line
        self.column = column

    def __str__(self):
        return f"Token({self.type}, {repr(self.value)}, {self.line}, {self.column})"

    def __iter__(self):
        return iter((self.type, self.value, self.line, self.column))
