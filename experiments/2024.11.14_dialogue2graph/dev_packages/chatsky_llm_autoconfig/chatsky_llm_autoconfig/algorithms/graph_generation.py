import json
from langchain.chat_models import ChatOpenAI
from langchain.output_parsers import PydanticOutputParser
from chatsky_llm_autoconfig.algorithms.base import GraphGenerator
from chatsky_llm_autoconfig.graph import BaseGraph, Graph
from chatsky_llm_autoconfig.schemas import DialogueGraph
from chatsky_llm_autoconfig.dialogue import Dialogue
from chatsky_llm_autoconfig.autometrics.registry import AlgorithmRegistry
from chatsky_llm_autoconfig.utils import call_llm_api, EnvSettings
from chatsky_llm_autoconfig.prompts import (
    prompts, graph_example_1, dialogue_example_2, graph_example_2
)

env_settings = EnvSettings()

@AlgorithmRegistry.register(input_type=Dialogue, path_to_result=env_settings.GENERATION_SAVE_PATH, output_type=BaseGraph)
class GeneralGraphGenerator(GraphGenerator):
    prompt_name: str = ""

    def __init__(self, prompt_name: str=""):
        super().__init__()
        self.prompt_name = prompt_name

    def invoke(self, dialogue: Dialogue = None, graph: DialogueGraph = None, topic: str = "") -> BaseGraph:

        model=ChatOpenAI(model=env_settings.GENERATION_MODEL_NAME, api_key=env_settings.OPENAI_API_KEY, base_url=env_settings.OPENAI_BASE_URL, temperature=1) | PydanticOutputParser(pydantic_object=DialogueGraph)
        #model=ChatOpenAI(model=env_settings.GENERATION_MODEL_NAME, api_key=env_settings.OPENAI_API_KEY, base_url=env_settings.OPENAI_BASE_URL, temperature=0)

        result = call_llm_api(prompts[self.prompt_name].format(graph_example_1=graph_example_1, dialogue_example_2=dialogue_example_2, graph_example_2=graph_example_2, dialog=dialogue.to_list()), model, temp=0)

        print("RESULT: ", result)

        result_graph = Graph(graph_dict=result.model_dump())
        #result_graph = Graph(graph_dict=json.loads(result))
        return result_graph

    async def ainvoke(self, *args, **kwargs):
        return self.invoke(*args, **kwargs)
