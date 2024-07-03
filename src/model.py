from langchain.prompts import PromptTemplate
from utils import call_llm_api
from prompts import create_graph_prompt, check_graph_utterances_prompt, check_graph_validity_prompt

class DialogModel:
    def __init__(self, client):
        self.client = client

    def create_graph(self, dialog, model_name="gpt-3.5-turbo", temp=0.3):
        graph = call_llm_api(
            create_graph_prompt.format(dialog=dialog),
            self.client,
            model_name,
            temp
        )
        return graph
    
    def check_graph_utterances(self, dialog, graph, model_name="gpt-3.5-turbo", temp=0.3):
        utterances = call_llm_api(
            check_graph_utterances_prompt.format(dialog=dialog, graph=graph),
            self.client,
            model_name,
            temp
        )
        return utterances
    
    def check_graph_validity(self, dialog, rules, model_name="gpt-3.5-turbo", temp=0.3):
        valid = call_llm_api(
            check_graph_validity_prompt.format(dialog=dialog, rules=rules),
            self.client,
            model_name,
            temp
        )
        return valid
    