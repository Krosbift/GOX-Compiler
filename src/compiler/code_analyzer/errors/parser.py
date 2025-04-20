from prettytable import PrettyTable
from colorama import Fore, Style


class ParserError:
    def __init__(self, errors):
        self.errors = errors

    def print_errors(self):
        table = self._create_error_table()
        print(table)
        return None

    def _create_error_table(self):
        table = PrettyTable()
        table.field_names = ["Num", "Type", "Value", "Line", "Column", "Message"]
        for i, (token, message) in enumerate(self.errors, start=1):
            color = Fore.RED
            table.add_row(self._format_error_row(i, token, message, color))
        return table

    def _format_error_row(self, index, token, message, color):
        return [
            index,
            f"{color}{token.type}{Style.RESET_ALL}",
            token.value,
            token.line,
            token.column,
            f"{color}{message}{Style.RESET_ALL}",
        ]
