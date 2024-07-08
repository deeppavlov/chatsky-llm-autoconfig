import random
import networkx as nx


def sample_dialogue(graph_obj: nx.DiGraph | nx.MultiDiGraph, start_node: int, topic: str = None):
    nodes = graph_obj.nodes(data=True)
    edges = graph_obj.edges(data=True)
    current_node_id = start_node
    current_node = nodes[current_node_id]
    dialogue = []
    graph = {"nodes": [], "edges": []}

    while True:

        utterance = random.choice(current_node["utterances"])
        dialogue.append({"text": utterance, "participant": "assistant"})


        graph['nodes'].append({
            "id": current_node_id,
            "label": graph_obj.nodes[current_node_id]['label'],
            "theme":  graph_obj.nodes[current_node_id]['theme'],
            "utterances": [utterance],
        })

        possible_edges = [e for e in edges if e[0] == current_node_id]
        if not possible_edges:
            break

        if topic is not None:
            chosen_edge = random.choice(possible_edges)
            # TODO this loop may be infinite
            while graph_obj.edges[chosen_edge[0], chosen_edge[1]]['theme'] != topic:
                chosen_edge = random.choice(possible_edges)

        if isinstance(chosen_edge[2]["utterances"], list):
            edge_utterance = random.choice(chosen_edge[2]["utterances"])
        else:
            edge_utterance = chosen_edge[2]["utterances"]

        dialogue.append({
            "text": edge_utterance, "participant": "user",
            "source": chosen_edge[0],
            "target": chosen_edge[1],
        })
    
        graph['edges'].append({
            "source": chosen_edge[0],
            "target": chosen_edge[1],
            "theme": graph_obj.edges[chosen_edge[0], chosen_edge[1]]['theme'],
            "utterances": [edge_utterance],
        })

        current_node_id = chosen_edge[1]
        current_node = nodes[current_node_id]
    return dialogue, graph


def sample_node_utterance(node: dict):
    res = random.choice(node["utterances"])
    return {"text": res, "participant": "assistant"}


def sample_edge_utterance(edge: dict):
    if isinstance(edge["utterances"], list):
        res = random.choice(edge["utterances"])
    else:
        res = edge["utterances"]
    return {"text": res, "participant": "user"}


def materialize_dialogue(graph_obj: nx.DiGraph | nx.MultiDiGraph, path: list[tuple[int,int]]):
    nodes = graph_obj.nodes()
    edges = graph_obj.edges()
    dialogue = []

    for src, tgt in path:
        dialogue.append(sample_node_utterance(nodes[src]))
        dialogue.append(sample_edge_utterance(edges[src, tgt]))
    
    dialogue.append(sample_node_utterance(nodes[tgt]))
    
    return dialogue
