import random
from chatsky_llm_autoconfig.graph import BaseGraph
from chatsky_llm_autoconfig.algorithms import DialogueGenerator
from chatsky_llm_autoconfig.dialogue import Dialogue

class DialogueSampler(DialogueGenerator):
    def invoke(self, graph: BaseGraph, start_node: int, end_node: int=-1, topic="") -> Dialogue:
        nodes = graph.graph.nodes(data=True)
        edges = graph.graph.edges(data=True)
        current_node_id = start_node
        current_node = nodes[current_node_id]
        dialogue = []
        graph_to_sample = {"nodes": [], "edges": []}

        while not (current_node_id == start_node and dialogue != []) or current_node_id == end_node:

            utterance = random.choice(current_node["utterances"])
            dialogue.append({"text": utterance, "participant": "assistant"})

            graph_to_sample["nodes"].append(
                {
                    "id": current_node_id,
                    "label": graph.nodes[current_node_id]["label"],
                    "theme": graph.nodes[current_node_id]["theme"],
                    "utterances": [utterance],
                }
            )

            possible_edges = [edge for edge in edges if edge[0] == current_node_id]
            if not possible_edges:
                break

            if topic is not None:
                chosen_edge = random.choice(possible_edges)
                while graph.edges[chosen_edge[0], chosen_edge[1]]["theme"] != topic:
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

            graph_to_sample["edges"].append(
                {
                    "source": chosen_edge[0],
                    "target": chosen_edge[1],
                    "theme": graph.edges[chosen_edge[0], chosen_edge[1]]["theme"],
                    "utterances": [edge_utterance],
                }
            )

            current_node_id = chosen_edge[1]
            current_node = nodes[current_node_id]
        return Dialogue(dialogue=dialogue)

    async def ainvoke(self, *args, **kwargs):
        return await super().ainvoke(*args, **kwargs)