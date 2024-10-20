from enum import Enum
import networkx as nx
from pydantic import BaseModel
from typing import Optional, Any, Union
import json
import matplotlib.pyplot as plt
import abc
import logging
logger = logging.getLogger(__name__)

class TYPES_OF_GRAPH(Enum):
    DI = 1  # if we do not allow multiedges
    MULTI = 2  # if we allow multiedges


class BaseGraph(BaseModel, abc.ABC):
    graph_dict: dict
    graph: Optional[nx.Graph] = None
    graph_type: Union[1, 2] = 1
    node_mapping: Optional[dict] = None

    class Config:
        arbitrary_types_allowed = True

    @abc.abstractmethod
    def load_graph(self, *args, **kwargs):
        raise NotImplementedError

    @abc.abstractmethod
    def visualise(self, *args, **kwargs):
        raise NotImplementedError

class Graph(BaseGraph):

    def __init__(self, graph_dict: dict, **kwargs: Any):
        super().__init__(graph_dict=graph_dict, **kwargs)  # Pass graph_dict to the parent class
        self.load_graph()

    def load_graph(self):
        self.graph = nx.MultiDiGraph() if self.graph_type == TYPES_OF_GRAPH.MULTI else nx.DiGraph()
        nodes = sorted([v["id"] for v in self.graph_dict["nodes"]])
        logging.debug(f"Nodes: {nodes}")

        self.node_mapping = {}
        renumber_flg = nodes != list(range(1, len(nodes) + 1))
        if renumber_flg:
            self.node_mapping = {node_id: idx + 1 for idx, node_id in enumerate(nodes)}
        logging.debug(f"Renumber flag: {renumber_flg}")


        for node in self.graph_dict["nodes"]:
            cur_node_id = node["id"]
            if renumber_flg:
                cur_node_id = self.node_mapping[cur_node_id]

            theme = node.get("theme")
            label = node.get("label")
            if type(node["utterances"]) is list:
                self.graph.add_node(cur_node_id, theme=theme, label=label, utterances=node["utterances"])
            else:
                self.graph.add_node(cur_node_id, theme=theme, label=label, utterances=[node["utterances"]])

        for link in self.graph_dict["edges"]:
            source = self.node_mapping.get(link["source"], link["source"])
            target = self.node_mapping.get(link["target"], link["target"])
            self.graph.add_edges_from([(source, target, {"theme": link.get("theme"), "utterances": link["utterances"]})])
        
    def visualise(self, *args, **kwargs):
        pos = nx.kamada_kawai_layout(self.graph)
        nx.draw(self.graph, pos, with_labels=False, node_color="lightblue", node_size=500, font_size=8, arrows=True)
        edge_labels = nx.get_edge_attributes(self.graph, "label")
        node_labels = nx.get_node_attributes(self.graph, "label")
        nx.draw_networkx_edge_labels(self.graph, pos, edge_labels=edge_labels, font_size=12)
        nx.draw_networkx_labels(self.graph, pos, labels=node_labels, font_size=10)

        plt.title(__name__)
        plt.axis("off")
        plt.show()

if __name__=="__main__":
    with open('/home/askatasuna/Документы/DeepPavlov/chatsky-llm-autoconfig/data/data.json') as f:
        d = json.load(f)
    g = Graph(d[0]["target_graph"])
    # g.visualise()