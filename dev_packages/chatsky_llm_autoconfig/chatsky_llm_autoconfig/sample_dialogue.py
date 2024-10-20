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


def dialogues_from_graph(graph, readable: bool=False):
    # Create a directed graph from the JSON input
    G = nx.DiGraph()
    
    # Add nodes and edges to the graph
    for node in graph['nodes']:
        # Ensure 'is_start' is included in the node attributes
        G.add_node(node['id'], label=node['label'], utterances=node['utterances'], is_start=node.get('is_start', False))
    
    for edge in graph['edges']:
        G.add_edge(edge['source'], edge['target'], utterances=edge['utterances'])
    
    # Start the dialogue from the starting node
    start_nodes = [node for node in G.nodes if G.nodes[node].get('is_start', True)]
    if not start_nodes:
        raise ValueError("No starting node found in the graph.")
    
    current_node = random.choice(start_nodes)  # Randomly select one of the starting nodes
    dialogue = []
    visited_nodes = set()  # Track visited nodes to prevent cycles
    
    # Generate a dialogue by traversing the graph
    while True:
        # Get the current node's utterances
        node_utterances = G.nodes[current_node]['utterances']
        # print("NODE:", node_utterances)
        dialogue.append(random.choice(node_utterances))  # Randomly select an utterance
        
        # Mark the current node as visited
        visited_nodes.add(current_node)
        
        # Get the next possible nodes to traverse
        next_nodes = list(G.successors(current_node))
        if not next_nodes:  # If there are no successors, break the loop
            break
        
        # Filter out already visited nodes to prevent cycles
        next_nodes = [node for node in next_nodes if node not in visited_nodes]
        if not next_nodes:  # If all next nodes have been visited, break the loop
            break
        
        next_node = random.choice(next_nodes)
        
        # Get the edge utterances between the current node and the next node
        edge_utterances = G[current_node][next_node]['utterances']
        # print("EDGE:", edge_utterances)
        dialogue.append(random.choice(edge_utterances)) 
        # Randomly select the next node to traverse
        current_node = next_node
    
    if readable:
        out = ""
        for i in range(len(dialogue)):
            if i % 2 == 0:
                out += f"ASSISTANT: {dialogue[i]}\n"
            else:
                out += f"USER: {dialogue[i]}\n"
        return out
    return dialogue


# path_prefix = "~/Документы/DeepPavlov/dff-llm-integration/"
# with open(f"{path_prefix}/dataset/theme_graph.json", "r") as f:
#     content = json.load(f)
# graph = Graph(content, TYPES_OF_GRAPH.DI)
# sampled_dialogue, sampled_base_graph = sample_dialogue(graph.nx_graph, start_node=1, end_node=9, topic="videogames")

# with open(f"{path_prefix}/dataset/theme_sampled_graph.json", "r") as g:
#     exisint_graph = json.load(g)

# dialogues = exisint_graph
# dict_to_dump = {"dialog_id": len(dialogues) + 1, "proposed_dialog": sampled_dialogue, "base_graph": sampled_base_graph}
# dialogues.append(dict_to_dump)

# with open(f"{path_prefix}/dataset/theme_sampled_graph.json", "w") as g:
#     json.dump(dialogues, g, indent=4)
