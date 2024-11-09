import os
import json
from langchain.chat_models import ChatOpenAI
from chatsky_llm_autoconfig.algorithms.base import GraphGenerator
from chatsky_llm_autoconfig.graph import DialogueGraph
from chatsky_llm_autoconfig.dialogue import Dialogue
from chatsky_llm_autoconfig.autometrics.registry import AlgorithmRegistry
from chatsky_llm_autoconfig.utils import call_llm_api, EnvSettings
from chatsky_llm_autoconfig.prompts import (
    general_graph_generation_prompt,
)

class DialogueDump(DialogueGraph):

    def save_json(self, file_path: str):
        if file_path:
            with open(file_path, 'w') as f:
                json.dump(self.model_dump(), f)

env_settings = EnvSettings()

@AlgorithmRegistry.register(input_type=Dialogue, output_type=DialogueGraph)
class CycleGraphGenerator(GraphGenerator):
    def invoke(self, dialogue: Dialogue = None, graph: DialogueGraph = None, topic: str = "") -> DialogueDump:
        """сохраняем результат и читаем, параметры сохранения,имя модели промпта"""


        model=ChatOpenAI(model="gpt-4o-mini", api_key=env_settings.OPENAI_API_KEY, base_url=env_settings.OPENAI_BASE_URL, temperature=0)

        graph = call_llm_api(general_graph_generation_prompt.format(dialog=dialogue.model_dump()['dialogue']), model, temp=0)

        return DialogueDump.model_validate_json(graph)


    async def ainvoke(self, *args, **kwargs):
        return self.invoke(*args, **kwargs)
