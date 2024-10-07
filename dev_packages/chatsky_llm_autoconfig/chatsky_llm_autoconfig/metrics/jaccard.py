import numpy as np


def collapse_multiedges(edges):
    collapsed_edges = {}
    for u, v, data in edges:
        key = f"{u}->{v}"
        if key not in collapsed_edges:
            collapsed_edges[key] = []
        if isinstance(data["utterances"], str):
            collapsed_edges[key].append(data["utterances"])
        elif isinstance(data["utterances"], list):
            collapsed_edges[key].extend(data["utterances"])
    return collapsed_edges


def jaccard_edges(true_graph_edges, generated_graph_edges, verbose=False, return_matrix=False):
    """
    true_graph_edges:Graph.edges - ребра истинного графа
    generated_graph_edges: nx.Graph.edges - ребра сгенерированного графу
    формат ребер:
    (1, 2, {"utterances": ...})
    verbose: bool - печать отладочной информации
    """
    true_graph_edges = collapse_multiedges(list(true_graph_edges))
    generated_graph_edges = collapse_multiedges(list(generated_graph_edges))

    jaccard_values = np.zeros((len(true_graph_edges), len(generated_graph_edges)))
    print(jaccard_values.shape)
    for idx1, (k1, v1) in enumerate(true_graph_edges.items()):
        for idx2, (k2, v2) in enumerate(generated_graph_edges.items()):
            value1 = set(v1).intersection(set(v2))
            value2 = set(v1).union(set(v2))
            jaccard_values[idx1][idx2] = len(value1) / len(value2)

            if verbose:
                print(k1, v1)
                print(k2, v2)
                print(value1, value2)
                print("___")
    if verbose:
        print(jaccard_values)
    max_jaccard_values = np.max(jaccard_values, axis=1)
    max_jaccard_indices = np.argmax(jaccard_values, axis=1)
    if return_matrix:
        return max_jaccard_values, max_jaccard_indices, jaccard_values
    return list(max_jaccard_values), list(max_jaccard_indices)


def get_list_of_node_utterances(node1_utterances):
    if type(node1_utterances) is str:
        return [node1_utterances]
    return node1_utterances


def collapse_multinodes(nodes):
    collapsed_nodes = {}
    for key, data in nodes:
        if key not in collapsed_nodes:
            collapsed_nodes[key] = []
        if isinstance(data["utterances"], str):
            collapsed_nodes[key].append(data["utterances"])
        elif isinstance(data["utterances"], list):
            collapsed_nodes[key].extend(data["utterances"])
    return collapsed_nodes


def jaccard_nodes(true_graph_nodes, generated_graph_nodes, verbose=False, return_matrix=False):
    """
    true_graph_nodes: Graph.nodes - вершины истинного графа
    generated_graph_nodes: nx.Graph.nodes - вершины сгенерированного графу
    формат вершин:
    (1, {"utterances": ...})
    verbose: bool - печать отладочной информации
    """
    true_graph_nodes = collapse_multinodes(list(true_graph_nodes))
    generated_graph_nodes = collapse_multinodes(list(generated_graph_nodes))

    jaccard_values = np.zeros((len(true_graph_nodes) + 1, len(generated_graph_nodes) + 1))
    print(true_graph_nodes)
    for node1_id, node1_utterances in true_graph_nodes.items():
        for node2_id, node2_utterances in generated_graph_nodes.items():
            node1_utterances = set(get_list_of_node_utterances(node1_utterances))
            node2_utterances = set(get_list_of_node_utterances(node2_utterances))

            jaccard_nominator = node1_utterances.intersection(node2_utterances)
            jaccard_denominator = node1_utterances.union(node2_utterances)

            jaccard_values[node1_id][node2_id] = len(jaccard_nominator) / len(jaccard_denominator)

            if verbose:
                print(node1_utterances)
                print(node2_utterances)
                print(jaccard_nominator, jaccard_denominator)
                print("_____")
    if verbose:
        print(jaccard_values)
    max_jaccard_values = np.max(jaccard_values[1:], axis=1)
    max_jaccard_indices = np.argmax(jaccard_values[1:], axis=1)
    max_jaccard_indices = max_jaccard_indices - np.ones(max_jaccard_indices.shape)
    np.place(max_jaccard_indices, max_jaccard_indices < 0, 0)
    max_jaccard_indices = max_jaccard_indices.astype(int)
    if return_matrix:
        return max_jaccard_values, max_jaccard_indices, jaccard_values[1:, 1:]
    return list(max_jaccard_values), list(max_jaccard_indices)
