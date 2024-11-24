"""
LLM Metrics.
------------

This module contains functions that checks Graphs and Dialogues for various metrics using LLM calls.
"""

from chatsky_llm_autoconfig.graph import BaseGraph
from langchain_core.language_models.chat_models import BaseChatModel
from langchain.prompts import PromptTemplate
from pydantic import BaseModel, Field
from langchain_core.output_parsers import PydanticOutputParser
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)


def are_triplets_valid(G: BaseGraph, model: BaseChatModel, topic: str) -> dict[str]:
    """
    Validates the dialog graph structure and logical transitions between nodes.

    Parameters:
        G (BaseGraph): The dialog graph to validate
        model (BaseChatModel): The LLM model to use for validation
        topic (str): The topic of the dialog

    Returns:
        dict: {'value': bool, 'description': str}
    """
    # Define prompt template and parser inside the function since they're only used here
    triplet_validate_prompt_template = """
        You are evaluating if a dialog transition is logically valid.

        Given a triplet of utterances:
        - source: assistant's phrase
        - edge: user's phrase 
        - target: assistant's next phrase

        TASK: Determine if the transition makes logical sense in any potential dialog context.

        Examples of INVALID transitions:

        1) Invalid because asks general question ignoring specific request:
        source: "Great! Your membership is set up. Would you like to know about our other facilities?"
        edge: "Can you tell me about other facilities?" 
        target: "What would you like to know about our gym?"

        2) Invalid because asks generic question instead of handling specific request:
        source: "Your appointment is confirmed. Thank you for choosing AutoCare!"
        edge: "Actually, I need to add a brake check"
        target: "What type of service do you need?"

        Review this transition for topic: {topic}
        source: {source_utterances}
        edge: {edge_utterances}
        target: {target_utterances}

        Reply in JSON format:
        {{"isValid": true/false, "description": "Brief explanation of why it's valid or invalid."}}"""

    triplet_validate_prompt = PromptTemplate(
        input_variables=["source_utterances", "edge_utterances", "target_utterances", "topic"],
        template=triplet_validate_prompt_template,
    )

    class TransitionValidationResult(BaseModel):
        isValid: bool = Field(description="Whether the transition is valid or not.")
        description: str = Field(description="Explanation of why it's valid or invalid.")

    parser = PydanticOutputParser(pydantic_object=TransitionValidationResult)

    graph = G.graph_dict
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
            logging.info(description)
            overall_valid = False
            descriptions.append(description)
            continue
        if target_id not in node_map:
            description = f"Invalid edge: target node {target_id} does not exist."
            logging.info(description)
            overall_valid = False
            descriptions.append(description)
            continue

        source_node = node_map[source_id]
        target_node = node_map[target_id]

        # Get utterances from nodes
        source_utterances = source_node.get("utterances", [])
        target_utterances = target_node.get("utterances", [])

        # Prepare input data for the chain
        input_data = {
            "source_utterances": source_utterances,
            "edge_utterances": edge_utterances,
            "target_utterances": target_utterances,
            "topic": topic,
        }

        triplet_check_chain = triplet_validate_prompt | model | parser
        response = triplet_check_chain.invoke(input_data)

        if not response.isValid:
            overall_valid = False
            description = f"Invalid transition from {source_utterances} to {target_utterances} via edge '{edge_utterances}': {response.description}"
            logging.info(description)
            descriptions.append(description)

    result = {"value": overall_valid, "description": " ".join(descriptions) if descriptions else "All transitions are valid."}
    return result


def is_theme_valid(G: BaseGraph, model: BaseChatModel, topic: str) -> dict[str]:
    """
    Validates if the dialog stays on theme/topic throughout the conversation.

    Parameters:
        G (BaseGraph): The dialog graph to validate
        model (BaseChatModel): The LLM model to use for validation
        topic (str): The expected topic of the dialog

    Returns:
        dict: {'value': bool, 'description': str}
    """

    class ThemeValidationResult(BaseModel):
        isValid: bool = Field(description="Whether the dialog stays on theme")
        description: str = Field(description="Explanation of why it's valid or invalid")

    theme_validate_prompt = PromptTemplate(
        input_variables=["utterances", "topic"],
        template="""
        You are given a dialog between assistant and a user.
        Analyze the following dialog and determine if it stays on the expected topic.
        
        Expected Topic: {topic}
        
        Dialog utterances:
        {utterances}
        
        Provide your answer in the following JSON format:
        {{"isValid": true or false, "description": "Explanation of why it's valid or invalid."}}

        Your answer:
        """,
    )

    parser = PydanticOutputParser(pydantic_object=ThemeValidationResult)

    # Extract all utterances from the graph
    graph = G.graph_dict
    all_utterances = []

    # Get assistant utterances from nodes
    for node in graph["nodes"]:
        all_utterances.extend(node.get("utterances", []))

    # Get user utterances from edges
    for edge in graph["edges"]:
        all_utterances.extend(edge.get("utterances", []))

    # Format utterances for the prompt
    formatted_utterances = "\n".join([f"- {utterance}" for utterance in all_utterances])

    # Prepare input data
    input_data = {"utterances": formatted_utterances, "topic": topic}

    # Create and run the chain
    theme_check_chain = theme_validate_prompt | model | parser
    response = theme_check_chain.invoke(input_data)

    return {"value": response.isValid, "description": response.description}
