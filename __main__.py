import argparse
from src.main import Main


class Init:
    @staticmethod
    def parse_arguments():
        """Parses command-line arguments for the GOX compiler.

        Returns
            argparse.Namespace: An object containing the parsed command-line arguments.
                - path_file (str): The path to the file to compile.
        """
        parser = argparse.ArgumentParser(description="gox-compiler")
        parser.add_argument("path_file", help="File to compile")
        return parser.parse_args()

    @staticmethod
    def init():
        """
        Initializes the compiler by parsing arguments and invoking the main compilation process.

        Raises
            SyntaxError: If no file path is provided for compilation.
        """
        args = Init.parse_arguments()
        if not args.path_file:
            raise SyntaxError("No file path provided for compilation")
        Main.main(args.path_file)


if __name__ == "__main__":
    Init.init()
