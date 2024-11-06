import json
import os
import numpy as np
import matplotlib.pyplot as plt
import networkx as nx
from langchain.chat_models import ChatOpenAI
from dotenv import load_dotenv
from chatsky_llm_autoconfig.model import DialogModel
from chatsky_llm_autoconfig.graph import Graph
from chatsky_llm_autoconfig.metrics.jaccard import jaccard_edges, jaccard_nodes
from chatsky_llm_autoconfig.metrics.automatic_metrics import triplet_match

load_dotenv()

# Initialize DialogModel
dialog_model = DialogModel()


def load_dialogues(file_path):
    with open(file_path, "r") as f:
        return json.load(f)


def generate_graph(dialogue, model_name):
    return json.loads(
        dialog_model.create_graph(
            dialogue, model=ChatOpenAI(model=model_name, api_key=os.getenv("OPENAI_API_KEY"), base_url=os.getenv("OPENAI_BASE_URL"), temperature=0)
        )
    )


def calculate_metrics(generated_graph, target_graph):
    true_graph = Graph(target_graph)
    gen_graph = Graph(generated_graph)

    # Calculate Jaccard similarity for edges and nodes
    edge_similarity, _ = jaccard_edges(true_graph.nx_graph.edges(data=True), gen_graph.nx_graph.edges(data=True))
    node_similarity, _ = jaccard_nodes(true_graph.nx_graph.nodes(data=True), gen_graph.nx_graph.nodes(data=True))

    # Calculate Triplet Match Accuracy
    node_mapping, edge_mapping = triplet_match(true_graph, gen_graph)

    # Calculate the accuracy based on the mappings
    total_nodes = len(true_graph.nx_graph.nodes())
    total_edges = len(true_graph.nx_graph.edges())
    matched_nodes = sum(1 for v in node_mapping.values() if v is not None)
    matched_edges = sum(1 for v in edge_mapping.values() if v is not None)

    node_accuracy = matched_nodes / total_nodes if total_nodes > 0 else 0
    edge_accuracy = matched_edges / total_edges if total_edges > 0 else 0

    # Calculate overall triplet match accuracy
    triplet_match_accuracy = (node_accuracy + edge_accuracy) / 2

    return {
        "Jaccard Edge Similarity": edge_similarity,
        "Jaccard Node Similarity": node_similarity,
        "Triplet Match Accuracy": triplet_match_accuracy,
        "Node Accuracy": node_accuracy,
        "Edge Accuracy": edge_accuracy,
    }


def has_cycle(graph):
    try:
        nx.find_cycle(graph)
        return True
    except nx.NetworkXNoCycle:
        return False


def visualize_graph(graph, title):
    G = nx.DiGraph()
    for node in graph["nodes"]:
        G.add_node(node["id"], label=node["label"])
    for edge in graph["edges"]:
        G.add_edge(edge["source"], edge["target"], label=edge["utterances"])

    pos = nx.kamada_kawai_layout(G)
    nx.draw(G, pos, with_labels=False, node_color="lightblue", node_size=500, font_size=8, arrows=True)
    edge_labels = nx.get_edge_attributes(G, "label")
    node_labels = nx.get_node_attributes(G, "label")
    nx.draw_networkx_edge_labels(G, pos, edge_labels=edge_labels, font_size=12)
    nx.draw_networkx_labels(G, pos, labels=node_labels, font_size=10)

    plt.title(title)
    plt.axis("off")


def save_graph_comparison(target_graph, generated_graph, output_path):
    plt.figure(figsize=(20, 10))
    plt.subplot(121)
    visualize_graph(target_graph, "Target Graph")
    plt.subplot(122)
    visualize_graph(generated_graph, "Generated Graph")
    plt.tight_layout()
    plt.savefig(output_path)
    plt.close()


def save_metrics(metrics, output_path):
    with open(output_path, "w") as f:
        json.dump(metrics, f, indent=2)


def calculate_mean_metrics(all_metrics):
    mean_triplet_match = np.mean([metrics["Triplet Match Accuracy"] for metrics in all_metrics.values()])
    mean_node_accuracy = np.mean([metrics["Node Accuracy"] for metrics in all_metrics.values()])
    mean_edge_accuracy = np.mean([metrics["Edge Accuracy"] for metrics in all_metrics.values()])

    return {"Mean Triplet Match Accuracy": mean_triplet_match, "Mean Node Accuracy": mean_node_accuracy, "Mean Edge Accuracy": mean_edge_accuracy}


def save_mean_metrics(mean_metrics, output_path):
    with open(output_path, "w") as f:
        for metric, value in mean_metrics.items():
            f.write(f"{metric}: {value:.4f}\n")


def evaluate_model(input_json_path, output_directory):
    os.makedirs(output_directory, exist_ok=True)

    dialogues = load_dialogues(input_json_path)
    all_metrics = {}

    for idx, dialogue in enumerate(dialogues):
        sample_dialogue = dialogue["dialog"]
        target_graph = dialogue["target_graph"]

        generated_graph = generate_graph(sample_dialogue)

        try:
            metrics = calculate_metrics(generated_graph, target_graph)
        except Exception as e:
            metrics = {"Triplet Match Accuracy": 0, "Node Accuracy": 0, "Edge Accuracy": 0}
            print(f"Invalid graph for dialogue {idx}")
            print(e)

        all_metrics[idx] = metrics

        save_graph_comparison(target_graph, generated_graph, f"{output_directory}/graph_comparison_{idx}.png")

    save_metrics(all_metrics, f"{output_directory}/all_metrics.json")

    mean_metrics = calculate_mean_metrics(all_metrics)
    save_mean_metrics(mean_metrics, f"{output_directory}/mean_metrics.txt")

    return f"{output_directory}/mean_metrics.txt"


def calculate_text_to_utterance_percentage(dialogue_graph_pair):
    dialogue = dialogue_graph_pair["dialog"]
    graph = dialogue_graph_pair["graph"]

    # Extract all texts from the dialogue
    dialogue_texts = set(turn["text"].lower() for turn in dialogue)

    # Extract all utterances from the graph
    graph_utterances = set()
    for edge in graph["edges"]:
        graph_utterances.update(utterance.lower() for utterance in edge["utterances"])
    for node in graph["nodes"]:
        if "utterances" in node:
            graph_utterances.update(utterance.lower() for utterance in node["utterances"])

    # Count how many dialogue texts are in graph utterances
    matched_texts = sum(1 for text in dialogue_texts if text in graph_utterances)

    # Calculate percentage
    percentage = (matched_texts / len(dialogue_texts)) * 100 if dialogue_texts else 0

    return percentage


def evaluate_generation(input_json_path, output_directory):
    os.makedirs(output_directory, exist_ok=True)
    data = load_dialogues(input_json_path)
    all_metrics = {
        "with_cycles": 0,
        "average_edges_amount": 0,
        "average_nodes_amount": 0,
        "total_graphs": 0,
        "total_edges": 0,
        "total_nodes": 0,
        "text_to_utterance_percentage": 0,
    }

    for _, dialogue in enumerate(data):
        gen_graph = dialogue["graph"]

        # Convert to NetworkX graph for analysis
        nx_graph = Graph(gen_graph).nx_graph

        # Check for cycles
        cycle = has_cycle(nx_graph)
        if cycle:
            all_metrics["with_cycles"] += 1

        # Count edges and nodes
        num_edges = nx_graph.number_of_edges()
        num_nodes = nx_graph.number_of_nodes()

        all_metrics["total_edges"] += num_edges
        all_metrics["total_nodes"] += num_nodes
        all_metrics["total_graphs"] += 1

        # Calculate text to utterance percentage
        percentage = calculate_text_to_utterance_percentage(dialogue)
        all_metrics["text_to_utterance_percentage"] += percentage

    # Calculate averages
    if all_metrics["total_graphs"] > 0:
        all_metrics["average_edges_amount"] = all_metrics["total_edges"] / all_metrics["total_graphs"]
        all_metrics["average_nodes_amount"] = all_metrics["total_nodes"] / all_metrics["total_graphs"]

    # Add percentage of graphs with cycles
    all_metrics["percentage_with_cycles"] = (all_metrics["with_cycles"] / all_metrics["total_graphs"]) * 100 if all_metrics["total_graphs"] > 0 else 0

    # Calculate average text to utterance percentage
    if all_metrics["total_graphs"] > 0:
        all_metrics["text_to_utterance_percentage"] = all_metrics["text_to_utterance_percentage"] / all_metrics["total_graphs"]

    # Save metrics to file
    with open(os.path.join(output_directory, "generation_metrics.json"), "w") as f:
        json.dump(all_metrics, f, indent=4)

    return all_metrics


if __name__ == "__main__":
    input_json_path = "data/data.json"
    output_directory = "experiments/results/gpt-4o-mini"
    report_file = evaluate_model(input_json_path, output_directory)
    print(f"Evaluation complete. Report saved to: {report_file}")
