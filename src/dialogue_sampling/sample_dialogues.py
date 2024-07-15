from typing import Iterable

import networkx as nx

from .cycles import add_cycles
from .topics import get_topics
from .utterance import materialize_dialogue, initialize_counters


def valid_topics(desired_topics: Iterable[str] | int | None, current_topics: set[str]):
    """check whether the number or set of topics is the same as desired"""
    if desired_topics is None:
        return True

    if isinstance(desired_topics, int):
        return desired_topics == len(current_topics)

    return set(desired_topics) == current_topics


def node_to_edge(path: list[int]) -> list[tuple[int, int]]:
    res = []
    for i in range(len(path) - 1):
        res.append((path[i], path[i + 1]))
    return res


def edge_to_node(path: list[tuple[int, int]]) -> list[int]:
    res = []
    for src, tgt in path:
        res.append(src)
    res.append(tgt)
    return res


def sample_dialogues(
    graph: nx.DiGraph,
    start_node: int,
    terminal_node: int,
    n: int = None,
    topics: Iterable[str] | int = None,
    n_cycles: int = None,
    n_repeats: Iterable[int] = None,
    uniqueness: float = 0,
):
    """
    Algorithm:
    - for each of `n` times:
        - find simple path from `start_node` to `terminal_node`
        - skip if path doesn't match given `topics` (set of topics or just number of topics)
        - add `n_cycles` and repeat them `n_repeats` times
        - meterialize dialogue by sampling utterances based on `uniqueness` measure (non-negative float, where `0` means uniform sampling, `>>1` means highly prioritized to avoid repeatitions)

    """
    graph = initialize_counters(graph)

    paths_generator = nx.all_simple_edge_paths(graph, start_node, terminal_node)

    res = []
    for path in paths_generator:
        current_topics = get_topics(graph, path)

        if not valid_topics(topics, current_topics):
            continue

        if n_cycles is not None and n_repeats is not None:
            path = edge_to_node(path)
            path = add_cycles(graph, path, n_cycles, n_repeats)
            if path is None:
                continue
            path = node_to_edge(path)

        dialog = materialize_dialogue(graph, path, uniqueness)
        res.append(dialog)

        if n is not None and len(res) == n:
            break

    return res
