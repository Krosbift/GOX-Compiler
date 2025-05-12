from prettytable import PrettyTable
from colorama import Fore, Style


class CheckerError:
    def __init__(self, errors):
        self.errors = errors

    def print_errors(self):
        table = self._create_error_table()
        print(table)
        return None

    def _create_error_table(self):
        table = PrettyTable()
        table.field_names = ["Num", "Message"]
        for i, error in enumerate(self.errors, start=1):
            color = Fore.RED
            if isinstance(error, tuple) and len(error) == 2:
                token, message = error
                table.add_row(self._format_error_row(i, token, message, color))
            else:
                table.add_row([i, f"{color}{error}{Style.RESET_ALL}"])
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
