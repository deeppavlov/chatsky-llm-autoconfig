from enum import Enum

class TYPES_OF_GRAPH(Enum):
    FULL = 1
    SEMI = 2
    DIFFERENT = 3

class Node:
    def __init__(self, id, is_start, label, response) -> None:
        self.id = id
        self.is_start = is_start
        self.response = response
        self.label = label

    def __eq__(self, other):
        if isinstance(other, Node):
            return self.response == other.response
        return False

    def __hash__(self):
        return hash(self.response)

    def __str__(self) -> str:
        return f"{self.id}: {self.response}"
    

class Link:
    def __init__(self, source: Node, target: Node) -> None:
        self.source = source
        self.target = target
        self.requests = []

    def add_response(self, response: str):
        if response not in self.requests:
            self.requests.append(response)

    def __str__(self) -> str:
        repr = "{self.source}->{self.target}:"
        for x in self.requests:
            repr+=x
        return repr

    def __repr__(self) -> str:
        repr = f"{self.source}->{self.target}:"
        for x in self.requests:
            repr+=x
        return repr
    
    def __eq__(self, other):
        if isinstance(other, Link):
            return self.source == other.source and self.target == other.target 
        return False