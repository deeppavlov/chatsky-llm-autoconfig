import numpy as np

def collapse_multiedges(edges):
    collapsed_edges = {}
    for u, v, data in edges:
        key=f'{u}->{v}'
        if key not in collapsed_edges:
            collapsed_edges[key] = []
        collapsed_edges[key].append(*data.values())
    return collapsed_edges

def jaccard_edges(edges1, edges2, verbose=False):
    edges1 = list(edges1)
    edges2 = list(edges2)
    
    collapsed_edges1 = collapse_multiedges(edges1)
    collapsed_edges2 = collapse_multiedges(edges2)

    jaccard_values = np.zeros((len(collapsed_edges1), len(collapsed_edges1)))
    
    for idx1, (k1, v1) in enumerate(collapsed_edges1.items()):
        for idx2, (k2, v2) in enumerate(collapsed_edges2.items()):
            value1 = set(v1).intersection(set(v2))
            value2 = set(v1).union(set(v2))

            if verbose:
                print(k1, v1)
                print(k2, v2)
                print(value1, value2)
                print("___")
            
            jaccard_values[idx1][idx2] = len(value1) / len(value2)
    if verbose:
        print(jaccard_values)
    max_jaccard_values = np.max(jaccard_values, axis=1)
    edges_maximising_jaccard_values = np.argmax(jaccard_values, axis=1)
    return max_jaccard_values, edges_maximising_jaccard_values


def jaccard_nodes(nodes1, nodes2, verbose=False):
    jaccard_values = np.zeros((len(nodes1) + 1, len(nodes2) + 1))
    for node1 in nodes1:
        for node2 in nodes2:
            
            node1_id = node1[0]
            node2_id = node2[0]

            if type(node1[1]['responses']) is str:
                node1_resp = [node1[1]['responses']]
            else:
                node1_resp = node1[1]['responses']

            if type(node2[1]['responses']) is str:
                node2_resp = [node2[1]['responses']]
            else:
                node2_resp = node2[1]['responses']                 

            value1 = set(node1_resp).intersection(set(node2_resp))
            value2 = set(node1_resp).union(set(node2_resp))
            
            jaccard_values[node1_id][node2_id] = len(value1) / len(value2)

            if verbose:
                print(node1[1]['responses'])
                print(node2[1]['responses'])
                print(value1, value2)
                print("_____")
    if verbose:
        print(jaccard_values)
    max_jaccard_values = np.max(jaccard_values, axis=1)
    nodes_maximising_jaccard_values = np.argmax(jaccard_values, axis=1)
    return max_jaccard_values, nodes_maximising_jaccard_values