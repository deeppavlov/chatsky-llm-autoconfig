from graph_src.graph import Graph
import networkx as nx
import random

# all func are currently unused
def check_if_nodes_identical(graph_1: Graph, graph_2: Graph):
       #check if we have the same amount of nodes:
    if len(graph_1.nodes) != len(graph_2.nodes):
        return False
    
    #check if the nodes are in the same 
    unmatched_1 = set(graph_1.nodes)
    unmatched_2 = set(graph_2.nodes)
    return unmatched_1 == unmatched_2

def check_if_links_identical(graph_1: Graph, graph_2: Graph):
    unmatched_first = []
    unmatched_second = []
    node_cnt = len(graph_1.nodes)
    for i in range(node_cnt):
        for j in range(node_cnt):
            if graph_1.transitions[i][j] is not None and graph_2.transitions[i][j] is not None:
                if graph_1.transitions[i][j].requests == graph_2.transitions[i][j].requests:
                    continue
                else:
                    if set(graph_1.transitions[i][j].requests) == set(graph_2.transitions[i][j].requests):
                        continue
                    else:
                        # print(graph_1.transitions[i][j].requests)
                        # print(graph_2.transitions[i][j].requests)
                        # raise ValueError("The target and source are identical, but the responses aren't")
                        unmatched_first.append((i,j,graph_1.transitions[i][j].requests))
                        unmatched_second.append((i,j,graph_2.transitions[i][j].requests))
            elif graph_1.transitions[i][j] is not None:
                unmatched_first.append((i,j,graph_1.transitions[i][j].requests))
            elif graph_2.transitions[i][j] is not None:
                unmatched_second.append((i,j,graph_2.transitions[i][j].requests))
            else:
                continue
    return unmatched_first, unmatched_second

def check_graph_isomorphism(graph1, graph2):
    flg = check_if_nodes_identical(graph1, graph2)
    if flg is False:
        return False
    a,b = check_if_links_identical(graph1, graph2)
    for e in a:
        print(e)
    print("_______")
    for e in b:
        print(e)
    print("_______")

def find_split_nodes(g1, g2):
    # Create dictionaries to map edges based on 'requests' attribute
    g1_requests = {}
    g2_requests = {}

    g1_edges = {}
    g2_edges = {}

    for u, v, data in g1.edges(data=True):
        request = data.get('requests')
        if request not in g1_requests:
            g1_requests[request] = []
        g1_requests[request].append((u, v))

    for u, v, data in g2.edges(data=True):
        request = data.get('requests')
        if request not in g2_requests:
            g2_requests[request] = []
        g2_requests[request].append((u, v))

    for u, v, data in g1.edges(data=True):
        key=f'{u}->{v}'
        if key not in g1_edges:
            g1_edges[key] = []
        g1_edges[key].append(*data.values())

    for u, v, data in g2.edges(data=True):
        key=f'{u}->{v}'
        if key not in g2_edges:
            g2_edges[key] = []
        g2_edges[key].append(*data.values())
    
    g1_split = {}
    g2_split = {}
    for edge, data in g1_edges.items():
        if len(data) > 1 and len(g2_edges[edge]) < len(data):
                g1_node = int(edge.split('->')[1])
                g2_end_nodes = []
                for request in data:
                    end_node = g2_requests[request][0][1]
                    g2_end_nodes.append(end_node)
                print(f"in g1 Node {g1_node} is split into {g2_end_nodes} in g2")
                g1_split[g1_node] = g2_end_nodes
    for edge, data in g2_edges.items():
        if len(data) > 1 and len(g1_edges[edge]) < len(data):
                g2_node = int(edge.split('->')[1])
                g1_end_nodes = []
                for request in data:
                    end_node = g1_requests[request][0][1]
                    g1_end_nodes.append(end_node)
                print(f"in g2 Node {g2_node} is split into {g1_end_nodes} in g1")
                g2_split[g2_node] = g1_end_nodes
                
    return g1_split,g2_split 

def do_mapping(g1, g2):
    if type(g1) is nx.MultiDiGraph():
        GM = nx.isomorphism.DiGraphMatcher(g1, g2, edge_match=lambda x, y: set(x['requests']).intersection(set( y['requests'])) is not None)
        are_isomorphic = GM.is_isomorphic()
    else:
        GM = nx.isomorphism.MultiDiGraphMatcher(g1, g2, edge_match=lambda x, y: set([elem['requests'] for elem in list(x.values())]).intersection(set([elem['requests'] for elem in list(y.values())])) is not None)
        are_isomorphic = GM.is_isomorphic()
    if are_isomorphic:
        print("Graphs are isomorphic and correct")
        mapping = nx.vf2pp_isomorphism(g1, g2, node_label=None)
        return mapping
    mapping = {}
    for i in range(1, len(g1.nodes)):
        mapping[i] = i
    g1_unmatched_nodes, g2_unmatched_nodes = find_split_nodes(g1, g2)
    print(g1_unmatched_nodes)
    print(g2_unmatched_nodes)
    for k, v in g1_unmatched_nodes.items():
        elem = random.choice(v)
        mapping[k] = elem
        for node in v:
            if node != elem:
                mapping[node] = None
    print(mapping)