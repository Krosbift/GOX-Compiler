import argparse
from .compiler import Compiler

class Main:
    @staticmethod
    def parse_args():
        """
        Analiza los argumentos de la línea de comandos.

        Devuelve:
            argparse.Namespace: Un objeto que contiene los argumentos de la línea de comandos analizados.
                - path_file (str): La ruta al archivo a compilar.
        """
        parser = argparse.ArgumentParser(description="GOX Compiler")
        parser.add_argument("path_file", help="Archivo a compilar")
        return parser.parse_args()

    @staticmethod
    def main():
        """
        Función principal para analizar los argumentos de la línea de comandos e invocar el compilador.

        Esta función utiliza el método `Main.parse_args()` para recuperar los argumentos de la línea de comandos
        y luego llama a la función `compiler` con la ruta del archivo proporcionada.
        """
        args = Main.parse_args()
        Compiler(args.path_file)
