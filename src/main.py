from .compiler import Compiler

class Main:
    @staticmethod
    def main(path_file: str):
        Compiler(path_file)
