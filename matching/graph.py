from enum import Enum
import networkx as nx

class TYPES_OF_GRAPH(Enum):
    DI = 1
    MULTI = 2

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
    
class Graph:
    def __init__(self, graph: dict, type: TYPES_OF_GRAPH) -> None:
        if type == TYPES_OF_GRAPH.MULTI:
            self.nx_graph = nx.MultiDiGraph()
        else:
            self.nx_graph = nx.DiGraph()
        node_count = len(graph['nodes'])
        self.type = type
        self.nodes = []
        self.transitions = [[None for _ in range(node_count + 1)] for _ in range(node_count + 1)]
        self.graph_degrees = []
        for node in graph['nodes']:
            self.nodes.append(Node(node['id'], node['is_start'], node['label'], node['response']))
            self.nx_graph.add_node(node['id'], request=node['response'])
        for link in graph['links']:
            first = link['source']
            second = link['target']
            link_obj = Link(first, second)
            link_obj.add_response(link['request'])
            self.transitions[first][second] = link_obj
            self.nx_graph.add_edges_from([(first, second, {"requests": link['request']})])
        for i in range(1, node_count + 1):
            self.graph_degrees.append(sum(1 for x in self.transitions[i] if x is not None))
