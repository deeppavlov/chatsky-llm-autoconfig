import os
import json
from pathlib import Path
from langchain.chat_models import ChatOpenAI
from langchain.output_parsers import PydanticOutputParser
from chatsky_llm_autoconfig.algorithms.base import GraphGenerator
from chatsky_llm_autoconfig.graph import DialogueGraph
from chatsky_llm_autoconfig.dialogue import Dialogue
from chatsky_llm_autoconfig.autometrics.registry import AlgorithmRegistry
from chatsky_llm_autoconfig.utils import call_llm_api, EnvSettings
from chatsky_llm_autoconfig.prompts import (
    prompts,
)

env_settings = EnvSettings()

@AlgorithmRegistry.register(input_type=Dialogue, use_saved=True, output_type=DialogueGraph)
class CycleGraphGenerator(GraphGenerator):
    def invoke(self, dialogue: Dialogue = None, graph: DialogueGraph = None, prompt_name="general_graph_generation_prompt", use_saved=True, topic: str = "") -> DialogueGraph:
        """сохраняем результат и читаем, параметры сохранения,имя модели промпта"""

        saved_data = {}
        if Path(env_settings.GENERATION_SAVE_PATH).is_file():
            with open(env_settings.GENERATION_SAVE_PATH) as f:
                try:
                    saved_data = json.load(f)
                except: pass

        if saved_data and use_saved:
            if env_settings.GENERATION_MODEL_NAME in saved_data and prompt_name in saved_data.get(env_settings.GENERATION_MODEL_NAME):
                result = saved_data.get(env_settings.GENERATION_MODEL_NAME).get(prompt_name)
                print("READ: ", result)
                if result:
                    return result

        model=ChatOpenAI(model=env_settings.GENERATION_MODEL_NAME, api_key=env_settings.OPENAI_API_KEY, base_url=env_settings.OPENAI_BASE_URL, temperature=0) | PydanticOutputParser(pydantic_object=DialogueGraph)

        graph = call_llm_api(prompts[prompt_name].format(dialog=dialogue.model_dump()['dialogue']), model, temp=0)
        print("GRAPH: ", graph)
        new_data = {env_settings.GENERATION_MODEL_NAME:{prompt_name:graph.model_dump()}}
        saved_data.update(new_data)
        with open(env_settings.GENERATION_SAVE_PATH, "w") as f:
            f.write(json.dumps(saved_data, indent=2, ensure_ascii=False))
        return graph
            #return DialogueDump.model_validate_json(graph)


    async def ainvoke(self, *args, **kwargs):
        return self.invoke(*args, **kwargs)
