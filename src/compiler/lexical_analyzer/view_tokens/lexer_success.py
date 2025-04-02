from prettytable import PrettyTable
from colorama import Fore, Style


class LexerSuccess:
    def __init__(self, tokens):
        self.tokens = tokens

    def print_tokens(self):
        table = self._create_token_table()
        print(table)
        return 0

    def _create_token_table(self):
        table = PrettyTable()
        table.field_names = ["Num", "Type", "Value", "Line", "Column"]
        for i, token in enumerate(self.tokens, start=1):
            color = Fore.GREEN
            table.add_row(self._format_token_row(i, token, color))
        return table

    def _format_token_row(self, index, token, color):
        return [
            index,
            f"{color}{token.type}{Style.RESET_ALL}",
            token.value,
            token.line,
            token.column,
        ]

    def _get_color_for_token(self, token_type):
        return {
            "IDENTIFIER": Fore.GREEN,
            "KEYWORD": Fore.BLUE,
            "LITERAL": Fore.CYAN,
        }.get(token_type, Fore.WHITE)
