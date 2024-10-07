import random
import json
from chatsky_llm_autoconfig.graph import Graph, TYPES_OF_GRAPH


def sample_dialogue(graph_obj, start_node, end_node=None, topic=None):
    nodes = graph_obj.nodes(data=True)
    edges = graph_obj.edges(data=True)
    current_node_id = start_node
    current_node = nodes[current_node_id]
    dialogue = []
    graph = {"nodes": [], "edges": []}
    appended_nodes = set()

    while not (current_node_id == start_node and dialogue != []) or current_node_id == end_node:

        utterance = random.choice(current_node["utterances"])
        dialogue.append({"text": utterance, "participant": "assistant"})

        graph["nodes"].append(
            {
                "id": current_node_id,
                "label": graph_obj.nodes[current_node_id]["label"],
                "theme": graph_obj.nodes[current_node_id]["theme"],
                "utterances": [utterance],
            }
        )

        possible_edges = [edge for edge in edges if edge[0] == current_node_id]
        if not possible_edges:
            break

        if topic is not None:
            chosen_edge = random.choice(possible_edges)
            while graph_obj.edges[chosen_edge[0], chosen_edge[1]]["theme"] != topic:
                chosen_edge = random.choice(possible_edges)

        if isinstance(chosen_edge[2]["utterances"], list):
            edge_utterance = random.choice(chosen_edge[2]["utterances"])
        else:
            edge_utterance = chosen_edge[2]["utterances"]

        dialogue.append(
            {
                "text": edge_utterance,
                "participant": "user",
                "source": chosen_edge[0],
                "target": chosen_edge[1],
            }
        )

        graph["edges"].append(
            {
                "source": chosen_edge[0],
                "target": chosen_edge[1],
                "theme": graph_obj.edges[chosen_edge[0], chosen_edge[1]]["theme"],
                "utterances": [edge_utterance],
            }
        )

        current_node_id = chosen_edge[1]
        current_node = nodes[current_node_id]
    return dialogue, graph


path_prefix = "~/Документы/DeepPavlov/dff-llm-integration/"
with open(f"{path_prefix}/dataset/theme_graph.json", "r") as f:
    content = json.load(f)
graph = Graph(content, TYPES_OF_GRAPH.DI)
sampled_dialogue, sampled_base_graph = sample_dialogue(graph.nx_graph, start_node=1, end_node=9, topic="videogames")

with open(f"{path_prefix}/dataset/theme_sampled_graph.json", "r") as g:
    exisint_graph = json.load(g)

dialogues = exisint_graph
dict_to_dump = {"dialog_id": len(dialogues) + 1, "proposed_dialog": sampled_dialogue, "base_graph": sampled_base_graph}
dialogues.append(dict_to_dump)

with open(f"{path_prefix}/dataset/theme_sampled_graph.json", "w") as g:
    json.dump(dialogues, g, indent=4)
