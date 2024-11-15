import networkx as nx
import random
import json
from chatsky_llm_autoconfig.graph import Graph
from langchain.schema import HumanMessage
from typing import Optional
from pydantic_settings import BaseSettings, SettingsConfigDict


class EnvSettings(BaseSettings, case_sensitive=True):

    model_config = SettingsConfigDict(env_file='experiments/2024.11.14_dialogue2graph/dev_packages/chatsky_llm_autoconfig/chatsky_llm_autoconfig/.env', env_file_encoding='utf-8')

    OPENAI_API_KEY: Optional[str]
    OPENAI_BASE_URL: Optional[str]
    GENERATION_MODEL_NAME: Optional[str]
    GENERATION_SAVE_PATH: Optional[str]
    TEST_DATA_PATH: Optional[str]
    RESULTS_PATH: Optional[str]
    EMBEDDER_MODEL: Optional[str]
    EMBEDDER_THRESHOLD: Optional[float]
    EMBEDDER_DEVICE: Optional[str]



# all func are currently unused
def check_if_nodes_identical(graph_1: Graph, graph_2: Graph):
    # check if we have the same amount of nodes:
    if len(graph_1.nodes) != len(graph_2.nodes):
        return False
    # check if the nodes are in the same
    return set(graph_1.nodes) == set(graph_2.nodes)


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
                        unmatched_first.append((i, j, graph_1.transitions[i][j].requests))
                        unmatched_second.append((i, j, graph_2.transitions[i][j].requests))
            elif graph_1.transitions[i][j] is not None:
                unmatched_first.append((i, j, graph_1.transitions[i][j].requests))
            elif graph_2.transitions[i][j] is not None:
                unmatched_second.append((i, j, graph_2.transitions[i][j].requests))
            else:
                continue
    return unmatched_first, unmatched_second


def check_graph_isomorphism(graph1, graph2):
    if not check_if_nodes_identical(graph1, graph2):
        return False

    unmatched_first, unmatched_second = check_if_links_identical(graph1, graph2)

    for edge in unmatched_first:
        print(edge)
    print("_______")
    for edge in unmatched_second:
        print(edge)
    print("_______")


def find_split_nodes(g1, g2):
    # Create dictionaries to map edges based on 'requests' attribute
    def map_edges_by_request(graph):
        requests_map = {}
        edges_map = {}
        for u, v, data in graph.edges(data=True):
            request = data.get("requests")
            if request not in requests_map:
                requests_map[request] = []
            requests_map[request].append((u, v))
            key = f"{u}->{v}"
            if key not in edges_map:
                edges_map[key] = []
            edges_map[key].append(*data.values())
        return requests_map, edges_map

    def find_splits(graph_edges, other_graph_edges, requests_map, graph_split, other_requests_map):
        for edge, data in graph_edges.items():
            if len(data) > 1 and len(other_graph_edges.get(edge, [])) < len(data):
                node = int(edge.split("->")[1])
                end_nodes = [other_requests_map[request][0][1] for request in data]
                graph_split[node] = end_nodes

    g1_requests, g1_edges = map_edges_by_request(g1)
    g2_requests, g2_edges = map_edges_by_request(g2)

    g1_split = {}
    g2_split = {}
    find_splits(g1_edges, g2_edges, g1_requests, g1_split, g2_requests)
    find_splits(g2_edges, g1_edges, g2_requests, g2_split, g1_requests)

    for node, split_nodes in g1_split.items():
        print(f"In g1, node {node} is split into {split_nodes} in g2")
    for node, split_nodes in g2_split.items():
        print(f"In g2, node {node} is split into {split_nodes} in g1")

    return g1_split, g2_split


def do_mapping(g1, g2):
    if isinstance(g1, nx.MultiDiGraph):
        GM = nx.isomorphism.DiGraphMatcher(g1, g2, edge_match=lambda x, y: set(x["requests"]).intersection(set(y["requests"])) is not None)
    else:
        GM = nx.isomorphism.MultiDiGraphMatcher(
            g1,
            g2,
            edge_match=lambda x, y: set([elem["requests"] for elem in list(x.values())]).intersection(
                set([elem["requests"] for elem in list(y.values())])
            )
            is not None,
        )

    if GM.is_isomorphic():
        print("Graphs are isomorphic and correct")
        mapping = nx.vf2pp_isomorphism(g1, g2, node_label=None)
        return mapping

    mapping = {i: i for i in range(1, len(g1.nodes))}
    g1_unmatched_nodes, g2_unmatched_nodes = find_split_nodes(g1, g2)
    print(g1_unmatched_nodes)
    print(g2_unmatched_nodes)
    for k, v in g1_unmatched_nodes.items():
        elem = random.choice(v)
        mapping[k] = elem
        for node in v:
            if node != elem:
                mapping[node] = None
    print(mapping)


def call_llm_api(query: str, llm, client=None, temp: float = 0.05, langchain_model=True) -> str | None:
    try:
        if langchain_model:
            messages = [HumanMessage(content=query)]
            response = llm.invoke(messages)
            return response
        else:
            messages.append({"role": "user", "content": query})
            response_big = client.chat.completions.create(
                model=llm,  # id модели из списка моделей - можно использовать OpenAI, Anthropic и пр. меняя только этот параметр
                messages=messages,
                temperature=0.7,
                n=1,
                max_tokens=3000,  # максимальное число ВЫХОДНЫХ токенов. Для большинства моделей не должно превышать 4096
                extra_headers={"X-Title": "My App"},  # опционально - передача информация об источнике API-вызова
            )
            return response_big.choices[0].message.content

    except Exception as e:
        print(e)
        print("Timeout error, retrying...")
        return None


def save_json(data: dict, filename: str) -> None:
    with open(filename, "w", encoding="utf-8") as file:
        json.dump(data, file, indent=4, ensure_ascii=False)


def read_json(path):
    with open(path, mode="r") as file:
        data = file.read()
    return json.loads(data)
