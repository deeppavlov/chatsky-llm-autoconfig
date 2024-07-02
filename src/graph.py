from enum import Enum
import networkx as nx


class TYPES_OF_GRAPH(Enum):
    DI = 1  # if we do not allow multiedges
    MULTI = 2  # if we allow multiedges


class Graph:
    def __init__(self, graph: dict, graph_type: TYPES_OF_GRAPH) -> None:
        self.nx_graph = nx.MultiDiGraph() if graph_type == TYPES_OF_GRAPH.MULTI else nx.DiGraph()
        self.type = graph_type
        nodes  = sorted([v['id'] for v in graph['nodes']])
        self.node_mapping = {}
        renumber_flg = nodes != list(range(1, len(nodes) + 1))
        if renumber_flg:
            self.node_mapping = {node_id: idx + 1 for idx, node_id in enumerate(nodes)}

        for node in graph['nodes']:
            cur_node_id = node['id']
            if renumber_flg:
                cur_node_id = self.node_mapping[cur_node_id]
            
            theme = node.get('theme')
            label = node.get('label')
            if type(node['utterances']) is list:
                self.nx_graph.add_node(cur_node_id, theme=theme, label=label, utterances=node['utterances'])
            else:
                self.nx_graph.add_node(cur_node_id, theme=theme, label=label, utterances=[node['utterances']])
        
        for link in graph['edges']:
            source = self.node_mapping.get(link['source'], link['source'])
            target = self.node_mapping.get(link['target'], link['target'])
            self.nx_graph.add_edges_from([(source, target, {"theme": link.get('theme'), "utterances": link['utterances']})])
