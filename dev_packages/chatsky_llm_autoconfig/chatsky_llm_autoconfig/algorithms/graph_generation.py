from langchain.prompts import PromptTemplate
#from langchain.chat_models import ChatOpenAI
from langchain_openai  import ChatOpenAI
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

#7) The cycle point(s) should make logical sense.
#8) One node or edge cannot have several utterances with different meanings and/or options.
#11) Number of nodes and edges cannot exceed number of unique utterances in dialogues.
#5) Use only utterances in their original form from the dialogues. It is prohibited to modify, cut or create new utterances different from input ones.
#4) Do not split one utterance between different nodes or edges.
#4) Never create nodes with user's utterances.
#5) Never create edges with assistance's utterances.
# 7) Number of nodes cannot exceed total number of unique assistant's utterances in all dialogues together.
# 8) Number of edges cannot exceed total number of unique user's utterances in all dialogues together.
# 12) The starting node of a cycle cannot be the entry point to the whole graph. It means that starting node typically does not have label "start" where is_start is True.
# Instead it must be a continuation of the user's previous phrase, kind of problem elaboration stage.
# Typically it is clarifying question to previous users' phrase.
# So cycle start cannot be greeting (first) node of the whole graph, it shall be another one node.
#6) Use only utterances in their original form from the dialogues. It is prohibited to modify, cut or create new utterances different from input ones.
#7) Don't create nodes or edges with utterances not present in any dialogue.
# 12) Cyclic graph means you don't duplicate nodes, but connect new edge to one of previously created nodes instead.
# When you go to next user's utterance, first try to answer to that utterance with utterance from one of previously created nodes.
# If you see it is possible not to create new node with same or similar utterance, but instead create next edge connecting back to that node, then it is place for a cycle here.
part_1 = """Your input is a list of dialogues from customer chatbot system.
Your task is to create a cyclic dialogue graph corresponding to these dialogues.
Next is an example of the graph (set of rules) how chatbot system looks like - it is
a set of nodes with chatbot system utterances and a set of edges that are
triggered by user requests: """
part_2 = """This is the end of the example.
Note that is_start field in the node is an entry point to the whole graph, not to the cycle.
**Rules:**
1) Nodes must be assistant's utterances, edges must be utterances from the user.
2) Every assistance's utterance from the dialogues shall be present in one and only one node of a graph.
3) Every user's utterance from the dialogues shall be present in one and only one edge of a graph.
4) Never create nodes with user's utterances.
5) Never create edges with assistance's utterances.
6) Every node or edge can have just one utterance.
7) Number of nodes is always equal to the number of unique assistant's utterances in all dialogues in total.
8) All edges must connect to existing nodes only.
9) Graph must be cyclic - shall contain cycle(s).
10) Different dialogues may contain various options that arise in the target graph.
So your task not to combine those alternatives in one node but to create new node for every option.
11) The starting node of a cycle typically does not have label "start" where is_start is true.
Instead it must be a continuation of the user's previous phrase, kind of problem elaboration stage.
Typically it is clarifying question to previous users' phrase.
12) Don't duplicate nodes or edges with same utterance.
13) You must always return valid JSON fenced by a markdown code block. Do not return any additional text.
14) Add reason point to the graph with an explanation when some nodes or edges have more than one utterance.
I will give a list of dialogues, your task is to build a graph for this list according to the rules and examples above.
List of dialogues: """

# part_1 = """Your input is a list of dialogues from customer chatbot system.
# Your task is to create a dialogue graph corresponding to these dialogues.
# If the dialogue is cyclic the graph shall be cyclic as well.
# Next is an example of the graph (set of rules) how chatbot system looks like - it is
# a set of nodes with chatbot system utterances and a set of edges that are
# triggered by user requests: """
# part_2 = """This is the end of the example.
# Note that is_start field in the node is an entry point to the whole graph, not to the cycle.
# **Rules:**
# 1) Nodes must be assistant's utterances, edges must be utterances from the user.
# 2) Every assistance's utterance from the dialogue shall be present in one and only one node of a graph. 
# 3) Every user's utterance from the dialogue shall be present in one and only one edge of a graph.
# 4) Use ony utterances from the dialogue. It is prohibited to create new utterances different from input ones.
# 5) Never create nodes with user's utterances.
# 6) Usually graph has branches, and different dialogues can present different branches.
# 7) The cycle point(s) should make logical sense.
# 8) The starting node of the cycle cannot be the beginning of a conversation with the user.
# It must be a continuation of the user's previous phrase, kind of problem elaboration stage.
# Typically it is clarifying question to previous users' phrase for example.
# So cycle start cannot be greeting (first) node of the whole graph, it shall be another one node.
# 9) Number of nodes and edges cannot exceed number of utterances in a dialogue.
# 10) You must always return valid JSON fenced by a markdown code block. Do not return any additional text.
# 11) Add reason point to the graph with explanation how cycle start points have been chosen.
# I will give a list of dialogues, your task is to build a graph for this list according to the rules and examples above.
# List of dialogues: """

# @AlgorithmRegistry.register(input_type=Dialogue, path_to_result=env_settings.GENERATION_SAVE_PATH, output_type=BaseGraph)
# class GeneralGraphGenerator(GraphGenerator):
#     prompt_name: str = ""

#     def __init__(self, prompt_name: str=""):
#         super().__init__()
#         self.prompt_name = prompt_name

#     def invoke(self, dialogue: Dialogue = None, graph: DialogueGraph = None, topic: str = "") -> BaseGraph:

#         model=ChatOpenAI(model=env_settings.GENERATION_MODEL_NAME, api_key=env_settings.OPENAI_API_KEY, base_url=env_settings.OPENAI_BASE_URL, temperature=1) | PydanticOutputParser(pydantic_object=DialogueGraph)
#         #model=ChatOpenAI(model=env_settings.GENERATION_MODEL_NAME, api_key=env_settings.OPENAI_API_KEY, base_url=env_settings.OPENAI_BASE_URL, temperature=0)

#         result = call_llm_api(prompts[self.prompt_name].format(graph_example_1=graph_example_1, dialogue_example_2=dialogue_example_2, graph_example_2=graph_example_2, dialog=dialogue.to_list()), model, temp=0)

#         # print("RESULT: ", result)
#         if result is None:
#             return Graph(graph_dict={})
#         result_graph = Graph(graph_dict=result.model_dump())
#         #result_graph = Graph(graph_dict=json.loads(result))
#         return result_graph

#     async def ainvoke(self, *args, **kwargs):
#         return self.invoke(*args, **kwargs)

@AlgorithmRegistry.register(input_type=list[Dialogue], path_to_result=env_settings.GENERATION_SAVE_PATH, output_type=BaseGraph)
class ListGraphGenerator(GraphGenerator):
    prompt_name: str = ""

    def __init__(self, prompt_name: str=""):
        super().__init__()
        self.prompt_name = prompt_name

    def invoke(self, dialogue: list[Dialogue] = None, graph: DialogueGraph = None, topic: str = "") -> BaseGraph:

        partial_variables = {}
        prompt_extra = ""
        for idx, dial in enumerate(dialogue):
            #partial_variables[f"var_{idx}"] = dial.to_list()
            partial_variables[f"var_{idx}"] = dial
            prompt_extra += f" Dialogue_{idx}: {{var_{idx}}}"
        prompt = PromptTemplate(template=part_1+"{graph_example_1}. "+prompt_extra, input_variables=["graph_example_1"], partial_variables=partial_variables)

        print("PROMPT: ", prompt)

        model=ChatOpenAI(model=env_settings.GENERATION_MODEL_NAME, api_key=env_settings.OPENAI_API_KEY, base_url=env_settings.OPENAI_BASE_URL, temperature=1) | PydanticOutputParser(pydantic_object=DialogueGraph)
        #model=ChatOpenAI(model=env_settings.GENERATION_MODEL_NAME, api_key=env_settings.OPENAI_API_KEY, base_url=env_settings.OPENAI_BASE_URL, temperature=0)

        result = call_llm_api(prompt.format(graph_example_1=graph_example_1), model, temp=0)

        # print("RESULT: ", result)
        if result is None:
            return Graph(graph_dict={})
        result_graph = Graph(graph_dict=result.model_dump())
        #result_graph = Graph(graph_dict=json.loads(result))
        return result_graph

    async def ainvoke(self, *args, **kwargs):
        return self.invoke(*args, **kwargs)
