from llm_autoconfig.utils import call_llm_api
from llm_autoconfig.prompts import create_graph_prompt, check_graph_utterances_prompt, check_graph_validity_prompt, cycle_graph_generation_prompt


class DialogModel:
    def __init__(self):
        pass

    def create_graph(self, dialog, model, temp=0.3):
        graph = call_llm_api(
            cycle_graph_generation_prompt.format(dialog=dialog),
            model,
            temp
        )
        return graph
    
    def check_graph_utterances(self, dialog, graph, model, temp=0.3):
        utterances = call_llm_api(
            check_graph_utterances_prompt.format(dialog=dialog, graph=graph),
            model,
            temp
        )
        return utterances
    
    def check_graph_validity(self, dialog, rules, model, temp=0.3):
        valid = call_llm_api(
            check_graph_validity_prompt.format(dialog=dialog, rules=rules),
            model,
            temp
        )
        return valid
    