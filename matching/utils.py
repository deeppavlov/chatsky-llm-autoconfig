from graph import Graph, Node, Link

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