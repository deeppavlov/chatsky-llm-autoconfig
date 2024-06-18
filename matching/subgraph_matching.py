import networkx as nx
from ..metric.metric_calc import jaccard_edges, collapse_multiedges

def edge_match_for_muligraph(x, y):
    set1 = set([elem['requests'] for elem in list(x.values())])
    set2 = set([elem['requests'] for elem in list(y.values())])
    return set1.intersection(set2) is not None 

def match(g1, g2):
    if type(g1) is nx.DiGraph():
        GM = nx.isomorphism.DiGraphMatcher(g1, g2, edge_match=lambda x, y: set(x['requests']).intersection(set(y['requests'])) is not None)
        are_isomorphic = GM.is_isomorphic()
    else:
        GM = nx.isomorphism.MultiDiGraphMatcher(g1, g2, edge_match=edge_match_for_muligraph)
        are_isomorphic = GM.is_isomorphic()
    if are_isomorphic:
        print("Graphs are isomorphic and correct")
        mapping = nx.vf2pp_isomorphism(g1, g2, node_label=None)
        return mapping
    
    mapping = {}

    edges1 = list(collapse_multiedges(g1.edges(data=True)).keys())
    edges2 = list(collapse_multiedges(g2.edges(data=True)).keys())

    _, _, matrix_edges = jaccard_edges(g1.edges(data=True), g2.edges(data=True), verbose=False)

    for i in range(matrix_edges.shape[0]):
        mapping[edges1[i]] = None
        for j in range (matrix_edges.shape[1]):
            if matrix_edges[i][j] > 0:
                node1_src, node1_trg = edges1[i].split('->')
                node2_src, node2_trg = edges2[j].split('->')
                # print(node1_src, node1_trg, node2_src, node2_trg)
                node1_src = g1.nodes[int(node1_src)]
                node2_src = g2.nodes[int(node2_src)]
                node1_trg = g1.nodes[int(node1_trg)]
                node2_trg = g2.nodes[int(node2_trg)]
                if node1_src['responses'] == node2_src['responses'] and \
                      node1_trg['responses'] != node2_trg['responses']:
                    print('Two edges has the same source but different targets')
                elif node1_src['responses'] != node2_src['responses'] or \
                      node1_trg['responses'] != node2_trg['responses']:
                    continue
                else:
                    mapping[edges1[i]] = edges2[j]