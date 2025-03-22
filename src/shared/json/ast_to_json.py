import json


class ASTtoJSON:
    @staticmethod
    def ast_to_dict(node):
        if isinstance(node, list):
            return [ASTtoJSON.ast_to_dict(n) for n in node]
        elif hasattr(node, "__dict__"):
            result = {}
            for key, value in node.__dict__.items():
                result[key] = ASTtoJSON.ast_to_dict(value)
            return result
        else:
            return node

    @staticmethod
    def convert_to_json(ast, output_file: str = "./tyson-ast.json"):
        ast_dict = ASTtoJSON.ast_to_dict(ast)
        with open(output_file, "w") as f:
            json.dump(ast_dict, f, indent=4)
