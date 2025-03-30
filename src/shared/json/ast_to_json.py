import json


class ASTtoJSON:
    @staticmethod
    def ast_to_dict(node):
        if isinstance(node, list):
            return [ASTtoJSON.ast_to_dict(n) for n in node]
        elif hasattr(node, "__dict__"):
            result = {"__class__": node.__class__.__name__}
            for key, value in node.__dict__.items():
                result[key] = ASTtoJSON.ast_to_dict(value)
            return result
        else:
            return node

    @staticmethod
    def convert_to_json(ast, file_name: str):
        output_name = "./" + file_name + ".output.json"
        ast_dict = ASTtoJSON.ast_to_dict(ast)
        with open(output_name, "w") as f:
            json.dump(ast_dict, f, indent=4)
