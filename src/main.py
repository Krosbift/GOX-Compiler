import argparse
from .compiler.compiler import Compiler


class Main:
    @staticmethod
    def init():
        args = Main.parse_arguments()
        if not args.path_file:
            raise SyntaxError(
                "No file path was provided for compilation"
            )
        Compiler(args.path_file)

    @staticmethod
    def parse_arguments():
        parser = argparse.ArgumentParser(description="gox-compiler")
        parser.add_argument("path_file", help="File to compile")
        return parser.parse_args()