from metric_calc import jaccard_nodes, jaccard_edges
from matching.graph import Graph, TYPES_OF_GRAPH
import json
import numpy as np


def load_graphs(test_name):
    with open(f'./{test_name}.json', 'r') as f:
        content = json.load(f)

    G1 = Graph(content['true'], TYPES_OF_GRAPH.MULTI).nx_graph
    G2 = Graph(content['generated'], TYPES_OF_GRAPH.MULTI).nx_graph
    return G1, G2


def test_single_nodes():
    true_graph, generated_graph = load_graphs('test_single_nodes')
    values, indices, matrix = jaccard_edges(true_graph.edges(data=True), generated_graph.edges(data=True),
                                            return_matrix=True)
    assert values == np.array([1.])
    assert indices == np.array([0])
    assert matrix == np.array([[1.]])

    values, indices = jaccard_nodes(true_graph.nodes(data=True), generated_graph.nodes(data=True),
                                    return_matrix=False)
    assert np.array_equal(values, np.array([1.]))
    assert np.array_equal(indices, np.array([0]))


def test_chain_with_equal_number_of_nodes():
    true_graph, generated_graph = load_graphs('test_chain_with_equal_number_of_nodes')
    values, indices, matrix = jaccard_edges(true_graph.edges(data=True), generated_graph.edges(data=True),
                                            return_matrix=True)

    assert np.array_equal(values, np.array([1., 1., 1., 1.]))
    assert np.array_equal(indices, np.array([0, 1, 2, 3]))
    assert np.array_equal(matrix, np.eye(4))

    values, indices = jaccard_nodes(true_graph.nodes(data=True), generated_graph.nodes(data=True),
                                    return_matrix=False)

    assert np.array_equal(values, np.array([0.5, 1., 0.5, 0.5, 2 / 3]))
    assert np.array_equal(indices, np.array([0, 1, 2, 3, 4]))



def test_cycle_with_missing_edge():
    true_graph, generated_graph = load_graphs('test_cycle_with_missing_edge')
    values, indices, matrix = jaccard_edges(true_graph.edges(data=True), generated_graph.edges(data=True),
                                            return_matrix=True)

    assert np.array_equal(values, np.array([1., 1., 1., 1., 0]))
    assert np.array_equal(indices, [0, 1, 2, 3, 0])
    m = np.array([[1., 0., 0., 0., ],
                  [0., 1., 0., 0.],
                  [0., 0., 1., 0.],
                  [0., 0., 0., 1.],
                  [0., 0., 0., 0.]])
    assert np.array_equal(matrix, m)

    values, indices, matrix = jaccard_nodes(true_graph.nodes(data=True), generated_graph.nodes(data=True),
                                            return_matrix=True)
    assert np.array_equal(values, np.array([1., 1., 1., 1.]))
    assert np.array_equal(indices, [0, 1, 2, 3])

def test_split_node():
    true_graph, generated_graph = load_graphs('test_split_node')
    values, indices, matrix = jaccard_edges(true_graph.edges(data=True), generated_graph.edges(data=True),
                                            return_matrix=True)
    assert np.array_equal(values, np.array([0.5, 0.5]))
    assert np.array_equal(indices, [0, 0])
    m = np.array([[0.5, 0],
                 [0.5, 0]])
    assert np.array_equal(matrix, m)
    values, indices, matrix = jaccard_nodes(true_graph.nodes(data=True), generated_graph.nodes(data=True),
                                            return_matrix=True)
    m = np.zeros((3,3))
    m[0][0] = 1.0
    assert np.array_equal(matrix, m)
    assert np.array_equal(values, np.array([1, 0, 0]))
    assert np.array_equal(indices, [0, 0, 0])
    # print(matrix)
    # print(values)
    # print(indices)

def test_complex_graph():
    true_graph, generated_graph = load_graphs('test_complex_graph')
    values, indices, matrix = jaccard_edges(true_graph.edges(data=True), generated_graph.edges(data=True),
                                            return_matrix=True)
    assert np.array_equal(values, np.array([1., 1., 1., 1., 1., 1., 1., 1., 1., 1., 1., 1.]))
    # assert np.array_equal(indices, [0, 0])
    m = np.array([[1., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0.],
       [0., 0., 1., 0., 0., 0., 0., 0., 0., 0., 0., 0.],
       [0., 1., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0.],
       [0., 0., 0., 0., 0., 1., 0., 0., 0., 0., 1., 0.],
       [0., 0., 0., 0., 0., 0., 1., 0., 1., 0., 0., 1.],
       [0., 0., 0., 1., 0., 0., 0., 0., 0., 0., 0., 0.],
       [0., 0., 0., 0., 1., 0., 0., 0., 0., 0., 0., 0.],
       [0., 0., 0., 0., 0., 1., 0., 0., 0., 0., 1., 0.],
       [0., 0., 0., 0., 0., 0., 1., 0., 1., 0., 0., 1.],
       [0., 0., 0., 0., 0., 0., 0., 1., 0., 0., 0., 0.],
       [0., 0., 0., 0., 0., 0., 1., 0., 1., 0., 0., 1.],
       [0., 0., 0., 0., 0., 0., 0., 0., 0., 1., 0., 0.]])
    assert np.array_equal(matrix, m)

    values, indices, matrix = jaccard_nodes(true_graph.nodes(data=True), generated_graph.nodes(data=True),
                                            return_matrix=True)
    assert np.array_equal(values, np.array([1., 1., 1., 1., 1., 1., 1., 1.]))
    
    
    m = np.array([[1., 0., 0., 0., 0., 0., 0., 0.],
                    [0., 1., 0., 0., 0., 0., 0., 0.],
                    [0., 0., 0., 0., 0., 0., 0., 1.],
                    [0., 0., 1., 0., 0., 0., 0., 0.],
                    [0., 0., 0., 1., 0., 0., 0., 0.],
                    [0., 0., 0., 0., 1., 0., 0., 0.],
                    [0., 0., 0., 0., 0., 1., 0., 0.],
                    [0., 0., 0., 0., 0., 0., 1., 0.]])
    assert np.array_equal(matrix, m)

test_single_nodes()
test_chain_with_equal_number_of_nodes()
test_cycle_with_missing_edge()
test_split_node()
test_complex_graph()