import random
import json
from graph_src.graph import Graph, TYPES_OF_GRAPH


def sample_dialogue(nodes, edges, start_node, end_node=None):
    # Find the start node
    current_node_id = start_node
    current_node = nodes[current_node_id]
    dialogue = []

    while not (current_node_id == start_node and dialogue != []) or current_node_id == end_node:
        utterance = random.choice(current_node["utterances"])
        dialogue.append({"text": utterance, "participant": "assistant"})
        possible_edges = [edge for edge in edges if edge[0] == current_node_id]

        if not possible_edges:
            break
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

        current_node_id = chosen_edge[1]
        current_node = nodes[current_node_id]
    return dialogue


path_prefix = '/Users/anastasia/Documents/DFF_LLM/dff-llm-integration/'
with open(f'{path_prefix}/dataset/theme_graph.json', 'r') as f:
    content = json.load(f)
graph = Graph(content, TYPES_OF_GRAPH.MULTI)
sampled_dialogue = sample_dialogue(graph.nx_graph.nodes(data=True), graph.nx_graph.edges(data=True), start_node=1,
                                   end_node=9)
with open(f'{path_prefix}/dataset/theme_sampled_graph.json', 'r') as g:
    exisint_graph = json.load(g)

dialogues = exisint_graph['dialogues']

dict_to_dump = {"dialog_id": len(dialogues) + 1, 'proposed_dialog': sampled_dialogue}
dialogues.append(dict_to_dump)

with open(f'{path_prefix}/dataset/theme_sampled_graph.json', 'w') as g:
    json.dump(dialogues, g, indent=4)
