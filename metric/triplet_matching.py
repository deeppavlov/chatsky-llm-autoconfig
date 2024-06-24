import networkx as nx
from metric.jaccard import jaccard_edges, jaccard_nodes, collapse_multiedges


def edge_match_for_muligraph(x, y):
    set1 = set([elem['requests'] for elem in list(x.values())])
    set2 = set([elem['requests'] for elem in list(y.values())])
    return set1.intersection(set2) is not None 


def parse_edge(edge):
    src, trg = edge.split('->')
    return int(src) - 1, int(trg) - 1


def triplet_match(g1, g2):
    node_mapping = {}
    for node in g1.nodes:
        node_mapping[node] = None
    for node in g2.nodes:
        node_mapping[node] = None
    if type(g1) is nx.DiGraph():
        GM = nx.isomorphism.DiGraphMatcher(g1, g2, edge_match=lambda x, y: set(x['requests']).intersection(set(y['requests'])) is not None)
        are_isomorphic = GM.is_isomorphic()
    else:
        GM = nx.isomorphism.MultiDiGraphMatcher(g1, g2, edge_match=edge_match_for_muligraph)
        are_isomorphic = GM.is_isomorphic()
    if are_isomorphic:
        print("Graphs are isomorphic")
        node_mapping = nx.vf2pp_isomorphism(g1, g2, node_label=None)
    
    edge_mapping = {}
    mapping_jaccard_values = {}

    edges1 = list(collapse_multiedges(g1.edges(data=True)).keys())
    edges2 = list(collapse_multiedges(g2.edges(data=True)).keys())

    _, _, matrix_edges = jaccard_edges(g1.edges(data=True), g2.edges(data=True), verbose=False, return_matrix=True)

    _, _, matrix_nodes = jaccard_nodes(g1.nodes(data=True), g2.nodes(data=True), verbose=False, return_matrix=True)


    for i in range(matrix_edges.shape[0]):
        edge_mapping[edges1[i]] = None
        mapping_jaccard_values[edges1[i]] = 0
        for j in range (matrix_edges.shape[1]):
            if matrix_edges[i][j] > 0:
                node1_src, node1_trg = parse_edge(edges1[i])
                node2_src, node2_trg = parse_edge(edges2[j])
                if matrix_nodes[node1_src][node2_src] == 0.0 and \
                    matrix_nodes[node1_trg][node2_trg] == 0.0:
                    continue
                elif matrix_nodes[node1_src][node2_src] > 0 and \
                    matrix_nodes[node1_trg][node2_trg] > 0:
                    if matrix_edges[i][j] > mapping_jaccard_values[edges1[i]]:
                        mapping_jaccard_values[edges1[i]] = matrix_edges[i][j]
                        edge_mapping[edges1[i]] = edges2[j]
                        node_mapping[node1_src + 1] = node2_src + 1
                        node_mapping[node1_trg + 1] = node2_trg + 1
                else:
                    node1_src_nx = g1.nodes[node1_src + 1]
                    node2_src_nx = g2.nodes[node2_src + 1]
                    if node1_src_nx == node2_src_nx:
                        node_mapping[node1_src + 1] = node2_src + 1
                    
                    node1_trg_nx = g1.nodes[node1_trg + 1]
                    node2_trg_nx = g2.nodes[node2_trg + 1]
                    if node1_trg_nx == node2_trg_nx:
                        node_mapping[node1_trg + 1] = node2_trg + 1
                    print(f'The nodes of edges {edges1[i]} and {edges2[j]} has something in common, but not complete match: Sources: {node1_src_nx["responses"]}, {node2_src_nx["responses"]}')
                    print(f'The nodes of edges {edges1[i]} and {edges2[j]} has something in common, but not complete match: Targets: {node1_trg_nx["responses"]}, {node2_trg_nx["responses"]}')
    return node_mapping, edge_mapping