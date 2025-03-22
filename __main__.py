import argparse
from src.main import Main


class Init:
    @staticmethod
    def parse_arguments():
        parser = argparse.ArgumentParser(description="gox-compiler")
        parser.add_argument("path_file", help="File to compile")
        return parser.parse_args()

    @staticmethod
    def init():
        args = Init.parse_arguments()
        if not args.path_file:
            raise SyntaxError(
                "No se proporcionó una ruta de archivo para la compilación"
            )
        Main.main(args.path_file)


if __name__ == "__main__":
    Init.init()
