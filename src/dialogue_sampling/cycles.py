import networkx as nx
from typing import Iterable


def find_possible_cycles(graph: nx.DiGraph | nx.MultiGraph, path: list[int]) -> list[list[int]]:
    """
    Find cycles in a `graph`, that have non empty intersection with `path`
    
    Arguments
    ---
    graph: networkx abstraction
    path: list of nodes on the path

    Result
    ---
    list of cycles, where one cycle is a list of nodes (e.g. [1,3,8])
    """
    path_nodes_set = set(path)
    all_cycles = nx.recursive_simple_cycles(graph)
    res = filter(
        lambda cycle: len(set(cycle) & path_nodes_set) > 0,
        all_cycles
    )
    return list(res)


def get_node2cycle_dict(cycles: list[list[int]]) -> dict[int, list[int]]:
    """mapping: node_id -> list of indexes of cycles where this node is occured"""
    res = {}
    for i_cycle, cycle in enumerate(cycles):
        for node_id in cycle:
            res[node_id] = res.get(node_id, []) + [i_cycle]
    return res


def cycle_shift_to_head(lst: list, head_elem):
    """make `head_elem` first in `lst` by performing cycle shift of array"""
    i = lst.index(head_elem)
    return lst[i:] + lst[:i]


def locate_cycles(cycles: list[list[int]], path: list[int]):
    """
    Returns list of cycles sorted in order of appearance on the path and index of node where to insert cycle

    Result
    ---
    sorted_cycles: list[list[int]]
    ids_within_path: list[int]
    """
    node2cycle = get_node2cycle_dict(cycles)    

    sorted_cycles = []
    ids_within_path = []

    for i, node_id in enumerate(path):
        cycle_ids = node2cycle.get(node_id, None)
        
        if not cycle_ids:
            continue
        
        # select cycles going through this node
        cur_cycles = [cycles[j] for j in cycle_ids]

        if i > 0:
            # check if this cycle already been added earlier
            cur_cycles = [c for c in cur_cycles if path[i-1] not in c]
        
        # preprocess
        if len(cur_cycles) > 0:
            cur_cycles = [cycle_shift_to_head(c, node_id) for c in cur_cycles]
            ids_within_path.extend([i] * len(cur_cycles))
            sorted_cycles.extend(cur_cycles)

    return sorted_cycles, ids_within_path


def repeat_and_insert_cycles(cycles: list[list[int]], path: list[int], indexes: list[int], n_repeats: list[int]):
    """
    insert `cycles` `n_repeats` times into places from `path` specified in `indexes`
    """
    res = path[:]
    n_repeats_gen = iter(n_repeats[::-1])
    
    # insert in reversed order to better deal with indexes
    for cycle, i in zip(cycles[::-1], indexes[::-1]):
        repeated_cycle = cycle * next(n_repeats_gen, n_repeats[-1])
        for node_id in repeated_cycle[::-1]:
            res.insert(i, node_id)

    return res


def add_cycles(nx_graph, path: list[int], n_cycles: int, n_repeats: Iterable[int], skip_when_impossible=True):
    """
    Add cycles to `path`.
    Algorithm:
        1. Find all cycles with non empty intersection with the `path`
        2. Arange cycles based on the order of appearance in the `path`
        3. Select first `n_cycles`
        4. Repeat them `n_repeats` (list of non-negative values) times and insert into path
    """
    assert n_cycles >= len(n_repeats)

    possible_cycles = find_possible_cycles(nx_graph, path)
    n_possible_cycles = len(possible_cycles)

    if n_cycles > n_possible_cycles:
        print(f'Warning: for path {path} demanded {n_cycles=} is larger than number of unique cycles that can be added to provided path ({n_possible_cycles=})')
        if skip_when_impossible:
            print(f'skipping this example, because {skip_when_impossible=}')
            return None
        else:
            print(f'set n_cycles to n_possible_cycles, because {skip_when_impossible=}')

        n_cycles = n_possible_cycles
        n_repeats = n_repeats[:n_cycles]
        cycles = possible_cycles
    else:
        cycles = possible_cycles[:n_cycles]

    cycles, indexes_to_insert = locate_cycles(cycles, path)
    res = repeat_and_insert_cycles(cycles, path, indexes_to_insert, n_repeats)

    return res