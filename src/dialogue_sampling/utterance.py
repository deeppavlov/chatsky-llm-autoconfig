import random

import networkx as nx
import numpy as np


def initialize_counters(graph: nx.DiGraph):
    """
    return copy of graph with every node and edge having attribute "n_times_visited"
    """
    graph = graph.copy()

    edges_counters = get_initial_counters(graph.edges)
    nx.set_edge_attributes(graph, edges_counters)

    nodes_counters = get_initial_counters(graph.nodes)
    nx.set_node_attributes(graph, nodes_counters)

    return graph


def get_initial_counters(edges_or_nodes):
    counters = {}
    for x in edges_or_nodes:
        n_utterances = len(edges_or_nodes[x]["utterances"])
        counters[x] = {"n_times_visited": [0] * n_utterances}
    return counters


def get_probs(statistics: list[int], alpha: float):
    """
    ```math
    p_i = P_i^alpha / (P_1^alpha + ... + P_N^alpha)
    ```
    """
    weights = (1 + statistics) ** (-alpha)
    probs = weights / np.sum(weights)
    return probs


def sample_node_utterance(node_id: int, alpha, graph: nx.DiGraph):
    node = graph.nodes[node_id]
    utterance, node = sample_utterance(node, alpha)
    nx.set_node_attributes(graph, values={node_id: node})   # update statistics
    return {"text": utterance, "participant": "assistant"}


def sample_edge_utterance(edge_id: tuple[int, int], alpha, graph: nx.DiGraph):
    edge = graph.edges[edge_id]
    utterance, node = sample_utterance(edge, alpha)
    nx.set_node_attributes(graph, values={edge_id: node})   # update statistics
    return {"text": utterance, "participant": "user"}


def sample_utterance(node_or_edge, alpha):
    # prob ~ 1 / number of times visited
    statistics = np.array(node_or_edge["n_times_visited"])
    probs = get_probs(statistics, alpha)

    # sample utterance
    utterances = node_or_edge["utterances"]
    i_utterance = random.choices(range(len(utterances)), weights=probs)[0]
    utterance = utterances[i_utterance]
    node_or_edge["n_times_visited"][i_utterance] += 1

    return utterance, node_or_edge


def materialize_dialogue(graph: nx.DiGraph, path: list[tuple[int, int]], alpha=0) -> list[dict[str,str]]:
    """
    Given edge `path` in `graph`, materialize dialogue by sampling node and edge utterances from path. Each utterance is sampled from distribution:
    ```math
    p_i = P_i^alpha / (P_1^alpha + ... + P_N^alpha)
    ```
    where
    - N is number of utterances binded to node/edge
    - P_i = 1 / number of times this utterance was sampled before 
    - `alpha` is non-negative float representing desired degree of uniqueness (0 is uniform sampling, >>1 is highly prioritized)
    """
    dialogue = []

    for src, tgt in path:
        dialogue.append(sample_node_utterance(src, alpha, graph))
        dialogue.append(sample_edge_utterance((src, tgt), alpha, graph))

    dialogue.append(sample_node_utterance(tgt, alpha, graph))

    return dialogue
