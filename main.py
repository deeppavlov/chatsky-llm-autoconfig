from llm_autoconfig.model import DialogModel
from llm_autoconfig.utils import call_llm_api
from llm_autoconfig.graph import Graph, TYPES_OF_GRAPH
from metrics.jaccard import jaccard_edges, jaccard_nodes
from metrics.triplet_matching import triplet_match
import json
import matplotlib.pyplot as plt
import networkx as nx
from openai import OpenAI
from langchain.chat_models import ChatOpenAI
import numpy as np
import os

from dotenv import load_dotenv
load_dotenv() 

# Initialize DialogModel
dialog_model = DialogModel()

def main():
    # Load all dialogues
    with open('data/cycles.json', 'r') as f:
        dialogues = json.load(f)

    all_metrics = {}
    directory = "experiments/results/gpt-4o-mini-cycles"
    for idx, dialogue in enumerate(dialogues):
        sample_dialogue = dialogue['dialog']
        target_graph = dialogue['target_graph']

        # Generate graph from dialogue
        generated_graph = dialog_model.create_graph(sample_dialogue, model=ChatOpenAI(model="gpt-4o-mini", api_key=os.getenv("OPENAI_API_KEY"), base_url=os.getenv("OPENAI_BASE_URL"), temperature=0))
        generated_graph = json.loads(generated_graph)

        # Calculate metrics
        try:
            metrics = calculate_metrics(generated_graph, target_graph)
        except:
            metrics = {"Triplet Match Accuracy": 0, "Node Accuracy": 0, "Edge Accuracy": 0}
            print(f"Invalid graph for dialogue {idx}")
        all_metrics[idx] = metrics

        # Visualize the generated and target graphs side by side
        plt.figure(figsize=(20, 10))
        plt.subplot(121)
        visualize_graph(target_graph, "Target Graph")
        plt.subplot(122)
        visualize_graph(generated_graph, "Generated Graph")
        plt.tight_layout()
        plt.savefig(f'{directory}/graph_comparison_{idx}.png')
        plt.close()

    with open(f'{directory}/all_metrics.json', 'w') as f:
        f.write(json.dumps(all_metrics, indent=2))
    with open(f'{directory}/mean_metrics.txt', 'w') as f:
        # Calculate mean values for each metric
        mean_triplet_match = np.mean([metrics['Triplet Match Accuracy'] for metrics in all_metrics.values()])
        mean_node_accuracy = np.mean([metrics['Node Accuracy'] for metrics in all_metrics.values()])
        mean_edge_accuracy = np.mean([metrics['Edge Accuracy'] for metrics in all_metrics.values()])

        report = f"""
        Mean Metrics:
        Triplet Match Accuracy: {mean_triplet_match:.4f}
        Node Accuracy: {mean_node_accuracy:.4f}
        Edge Accuracy: {mean_edge_accuracy:.4f}
        """
        f.write(report)
    
        # print("All metrics:", json.dumps(all_metrics, indent=2))
    # Plot metrics
    # plot_metrics(all_metrics)


def calculate_metrics(generated_graph, target_graph):
    true_graph = Graph(target_graph, TYPES_OF_GRAPH.MULTI)
    gen_graph = Graph(generated_graph, TYPES_OF_GRAPH.MULTI)

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
        "Edge Accuracy": edge_accuracy
    }

def visualize_graph(graph, title):
    G = nx.DiGraph()
    for node in graph['nodes']:
        G.add_node(node['id'], label=node['label'])
    for edge in graph['edges']:
        G.add_edge(edge['source'], edge['target'], label=edge['utterances'])

    pos = nx.spring_layout(G)
    nx.draw(G, pos, with_labels=True, node_color='lightblue', node_size=500, font_size=8, arrows=True)
    edge_labels = nx.get_edge_attributes(G, 'label')
    nx.draw_networkx_edge_labels(G, pos, edge_labels=edge_labels, font_size=6)
    plt.title(title)
    plt.axis('off')

def plot_metrics(all_metrics):
    metrics = list(all_metrics.keys())
    n_metrics = len(metrics)
    n_samples = max(len(values) for values in all_metrics.values())

    fig, ax = plt.subplots(figsize=(12, 6))
    width = 0.35
    x = np.arange(n_samples)

    for i, metric in enumerate(metrics):
        values = all_metrics[metric]
        # Pad the values array with NaN if it's shorter than the maximum length
        padded_values = values + [float('nan')] * (n_samples - len(values))
        ax.bar(x + i*width, padded_values, width, label=metric)

    ax.set_xlabel('Sample')
    ax.set_ylabel('Score')
    ax.set_title('Metrics Comparison')
    ax.set_xticks(x + width * (n_metrics - 1) / 2)
    ax.set_xticklabels([f'Sample {i+1}' for i in range(n_samples)])
    ax.legend()

    plt.tight_layout()
    plt.show()

if __name__ == "__main__":
    main()