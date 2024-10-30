"""
LLM Metrics.
------------

This module contains functions that checks Graphs and Dialogues for various metrics using LLM calls.
"""

from chatsky_llm_autoconfig.graph import BaseGraph
from typing import List, Tuple
from langchain_core.language_models.chat_models import BaseChatModel
from langchain.prompts import PromptTemplate
from pydantic import BaseModel, Field
from typing import List
from langchain_core.output_parsers import PydanticOutputParser


def are_triplets_valid(G: BaseGraph, model: BaseChatModel, topic: str) -> dict[str]:
    """
    Validates the dialog graph structure and logical transitions between nodes.

    Parameters:
        graph (dict): A dictionary containing 'nodes' and 'edges' of the graph.
        topic (str): The topic of the dialog.

    Returns:
        dict: {'value': bool, 'description': str}
    """
    graph = G.graph
    # Create a mapping from node IDs to node data for quick access
    node_map = {node["id"]: node for node in graph["nodes"]}
    overall_valid = True
    descriptions = []

    for edge in graph["edges"]:
        source_id = edge["source"]
        target_id = edge["target"]
        edge_utterances = edge["utterances"]

        # Check if source and target nodes exist
        if source_id not in node_map:
            description = f"Invalid edge: source node {source_id} does not exist."
            print(description)
            overall_valid = False
            descriptions.append(description)
            continue
        if target_id not in node_map:
            description = f"Invalid edge: target node {target_id} does not exist."
            print(description)
            overall_valid = False
            descriptions.append(description)
            continue

        source_node = node_map[source_id]
        target_node = node_map[target_id]

        # Get utterances from nodes
        source_utterances = source_node.get("utterances", [])
        target_utterances = target_node.get("utterances", [])

        # Validate the transition
        isValid, description = __validate_transition(source_utterances, edge_utterances, target_utterances, topic, model)
        if not isValid:
            overall_valid = False
            description = f"Invalid transition from {source_utterances} to {target_utterances} via edge '{edge_utterances}': {description}"
            print(description)
            descriptions.append(description)

    result = {"value": overall_valid, "description": " ".join(descriptions) if descriptions else "All transitions are valid."}
    return result


triplet_validate_prompt_template = """
You are given a dialog between assistant and a user.
source_utterances, edge_utterances, target_utterances are dialog parts and each contains an array with exactly one utterance.
They should be read left to right.

- source_utterances are assistant phrases 
- edge_utterances are user phrases
- target_utterances are assistant phrases 

TASK. Evaluate if the transition makes a logical connection when reading from Source utterances to Target utterances through Edge utterances

this is an invalid transition:
{{
    'source_utterances': ['Welcome to our online bookstore. How can I assist you today?'],
    'edge_utterances': ['Hello! Are you looking for any book recommendations?'],
    'target_utterances': ['We have a wide selection of genres. Which do you prefer?'],
    'topic': 'Dialog about purchasing books between assistant and customer'
}}

Provide your answer in the following JSON format:
{{"isValid": true or false, "description": "Explanation of why it's valid or invalid."}}

Dialog topic: {topic}

(source_utterances) {source_utterances} -> (edge_utterances) {edge_utterances} -> (target_utterances) {target_utterances}

Your answer:"""

triplet_validate_prompt = PromptTemplate(
    input_variables=["source_utterances", "edge_utterances", "target_utterances", "topic"],
    template=triplet_validate_prompt_template,
)


class TransitionValidationResult(BaseModel):
    isValid: bool = Field(description="Whether the transition is valid or not.")
    description: str = Field(description="Explanation of why it's valid or invalid.")


parser = PydanticOutputParser(pydantic_object=TransitionValidationResult)


def __validate_transition(
    source_utterances: List[str], edge_utterances: str, target_utterances: List[str], topic: str, model: BaseChatModel
) -> Tuple[bool, str]:
    """
    Validates a single transition in the graph using the language model.

    Parameters:
        source_utterances (List[str]): Utterances from the source node (assistant).
        edge_utterance (str): The utterance on the edge (user).
        target_utterances (List[str]): Utterances from the target node (assistant).
        topic (str): The topic of the dialog.

    Returns:
        Tuple[bool, str]: isValid and description.
    """
    # Prepare input data for the chain
    input_data = {"source_utterances": source_utterances, "edge_utterances": edge_utterances, "target_utterances": target_utterances, "topic": topic}

    triplet_check_chain = prompt | model | parser

    response = triplet_check_chain.invoke(input_data)

    isValid = response.isValid
    description = response.description
    return isValid, description
