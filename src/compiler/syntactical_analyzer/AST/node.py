from multimethod import multimeta
from dataclasses import dataclass


class Visitor(metaclass=multimeta):
    pass


@dataclass
class Node:
    def accept(self, v: Visitor):
        return v.visit(self)
