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
        nodes  = sorted([v['id'] for v in graph['nodes']])
        self.node_mapping = {}
        renumber_flg = False
        if nodes != [i for i in range(1, len(nodes) + 1)]:
            renumber_flg = True
            for j in range(len(nodes)):
                self.node_mapping[nodes[j]] = j + 1


        for node in graph['nodes']:
            cur_node_id = node['id']
            if renumber_flg:
                cur_node_id = self.node_mapping[cur_node_id]
            
            theme = node.get('theme')
            if type(node['utterances']) is list:
                self.nx_graph.add_node(cur_node_id, theme=theme, utterances=node['utterances'])
            else:
                self.nx_graph.add_node(cur_node_id, theme=theme, utterances=[node['utterances']])
    
        
        for link in graph['edges']:
                first = link['source']
                second = link['target']
                if renumber_flg:
                    first = self.node_mapping[first]
                    second = self.node_mapping[second]
                theme = link.get('theme')
                self.nx_graph.add_edges_from([(first, second, {"theme": theme,
                                                                "utterances": link['utterances']})])
