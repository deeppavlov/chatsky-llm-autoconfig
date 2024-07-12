import networkx as nx


def get_topics(graph: nx.DiGraph | nx.MultiGraph, path: list[tuple[int, int]]):
    edges = graph.edges()
    res = set(edges[src, tgt]['theme']for src, tgt in path)
    return res
