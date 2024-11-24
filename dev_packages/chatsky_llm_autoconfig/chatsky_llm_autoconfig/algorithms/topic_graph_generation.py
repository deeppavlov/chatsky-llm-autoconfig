from typing import Optional
from chatsky_llm_autoconfig.algorithms.base import TopicGraphGenerator
from chatsky_llm_autoconfig.autometrics.registry import AlgorithmRegistry
from chatsky_llm_autoconfig.schemas import DialogueGraph
from langchain_openai import ChatOpenAI

from langchain.prompts import PromptTemplate
from langchain_core.output_parsers import JsonOutputParser

from chatsky_llm_autoconfig.graph import BaseGraph, Graph
import os

from pydantic import SecretStr


@AlgorithmRegistry.register(input_type=str, output_type=BaseGraph)
class CycleGraphGenerator(TopicGraphGenerator):
    """Generator specifically for topic-based cyclic graphs"""

    prompt: str = ""
    cycle_graph_generation_prompt: str = ""


    def __init__(self, prompt: Optional[PromptTemplate] = None):
            super().__init__()
            self.cycle_graph_generation_prompt = prompt if prompt else PromptTemplate.from_template(
                """
        Create a cyclic dialogue graph where the conversation MUST return to an existing node.

        **CRITICAL: Response Specificity**
        Responses must acknowledge and build upon what the user has already specified:

        INCORRECT flow:
        - User: "I'd like to order a coffee"
        - Staff: "What would you like to order?" (TOO GENERAL - ignores that they specified coffee)

        CORRECT flow:
        - User: "I'd like to order a coffee"
        - Staff: "What kind of coffee would you like?" (GOOD - acknowledges they want coffee)

        Example of a CORRECT cyclic graph for a coffee shop:
        "edges": [
            {{ "source": 1, "target": 2, "utterances": ["Hi, I'd like to order a coffee"] }},
            {{ "source": 2, "target": 3, "utterances": ["A large latte please"] }},
            {{ "source": 3, "target": 4, "utterances": ["Yes, that's correct"] }},
            {{ "source": 4, "target": 5, "utterances": ["Here's my payment"] }},
            {{ "source": 5, "target": 2, "utterances": ["I'd like to order another coffee"] }}
        ],
        "nodes": [
            {{ "id": 1, "label": "welcome", "is_start": true, "utterances": ["Welcome! How can I help you today?"] }},
            {{ "id": 2, "label": "ask_coffee_type", "is_start": false, "utterances": ["What kind of coffee would you like?"] }},
            {{ "id": 3, "label": "confirm", "is_start": false, "utterances": ["That's a large latte. Is this correct?"] }},
            {{ "id": 4, "label": "payment", "is_start": false, "utterances": ["Great! That'll be $5. Please proceed with payment."] }},
            {{ "id": 5, "label": "completed", "is_start": false, "utterances": ["Thank you! Would you like another coffee?"] }}
        ]

        **Rules:**
        1) Responses must acknowledge what the user has already specified
        2) The final node MUST connect back to an existing node
        3) Each node must have clear purpose
        4) Return ONLY the JSON without commentary
        5) Graph must be cyclic - no dead ends
        6) All edges must connect to existing nodes
        7) The cycle point should make logical sense

        **Your task is to create a cyclic dialogue graph about the following topic:** {topic}.
        """
            )



    def invoke(self, topic: str) -> BaseGraph:
        """
        Generate a cyclic dialogue graph based on the topic input.

        :param input_data: TopicInput containing the topic
        :return: Generated Graph object with cyclic structure
        """
        parser = JsonOutputParser(pydantic_object=DialogueGraph)
        model = ChatOpenAI(model="gpt-4o", api_key=SecretStr(os.getenv("OPENAI_API_KEY") or ""), base_url=os.getenv("OPENAI_BASE_URL"), temperature=0)
        chain = self.cycle_graph_generation_prompt | model | parser

        generated_graph = chain.invoke({"topic": topic})

        return Graph(generated_graph)

    async def ainvoke(self, *args, **kwargs):
        pass


if __name__ == "__main__":
    cycle_graph_generator = CycleGraphGenerator()
