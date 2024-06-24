from enum import Enum
import networkx as nx


class TYPES_OF_GRAPH(Enum):
    DI = 1  # if we do not allow multiedges
    MULTI = 2  # if we allow multiedges


class Graph:
    def __init__(self, graph: dict, graph_type: TYPES_OF_GRAPH) -> None:
        if graph_type == TYPES_OF_GRAPH.MULTI:
            self.nx_graph = nx.MultiDiGraph()
        else:
            self.nx_graph = nx.DiGraph()
        self.type = graph_type
        self.graph_degrees = []
        for node in graph['nodes']:
            if type(node['utterances']) is list:
                self.nx_graph.add_node(node['id'], utterances=node['utterances'])
            else:
                self.nx_graph.add_node(node['id'], utterances=[node['utterances']])
        for link in graph['edges']:
            first = link['source']
            second = link['target']
            self.nx_graph.add_edges_from([(first, second, {"utterances": link['utterances']})])
