import random
import json
from graph_src.graph import Graph, TYPES_OF_GRAPH

def sample_dialogue(nodes, edges, start_node):
    # Find the start node
    current_node_id = start_node
    current_node = nodes[current_node_id]
    dialogue = []

    while not (current_node_id == start_node and dialogue != []):
        # Sample a random utterance from the current node
        utterance = random.choice(current_node["utterances"])
        dialogue.append({"text": utterance, "participant": "assistant"})
        
        # Find possible edges from the current node
        possible_edges = [edge for edge in edges if edge[0] == current_node_id]
        
        if not possible_edges:
            break  # No more transitions available, end the dialogue
        
        # Randomly choose an edge and its utterance
        chosen_edge = random.choice(possible_edges)
        if isinstance(chosen_edge[2]["utterances"], list):
            edge_utterance = random.choice(chosen_edge[2]["utterances"])
        else:
            edge_utterance = chosen_edge[2]["utterances"]
        dialogue.append({"text": edge_utterance, "participant": "user"})
        
        # Move to the target node
        current_node_id = chosen_edge[1]
        current_node = nodes[current_node_id]
        
    return dialogue


with open('dataset/graphs.json', 'r') as f:
    content = json.load(f)
dialog_id = '5'
graph = Graph(content[dialog_id], TYPES_OF_GRAPH.MULTI)
sampled_dialogue = sample_dialogue(graph.nx_graph.nodes(data=True), graph.nx_graph.edges(data=True), start_node=1)
dict_to_dump = {"dialog_id": dialog_id, 'proposed_dialog': sampled_dialogue}
with open('dataset/sampled_graphs.json', 'a') as g:
    json.dump(dict_to_dump, g, indent=4)