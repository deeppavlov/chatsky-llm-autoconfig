from chatsky_llm_autoconfig.autometrics.registry import AlgorithmRegistry
import chatsky_llm_autoconfig.sample_dialogue
import json
from chatsky_llm_autoconfig.graph import Graph, BaseGraph
from chatsky_llm_autoconfig.dialogue import Dialogue
from chatsky_llm_autoconfig.metrics.automatic_metrics import *
import datetime


with open('dev_packages/chatsky_llm_autoconfig/chatsky_llm_autoconfig/autometrics/test_data/data.json') as f:
    test_data = json.load(f)
    test_dialogue = test_data['dialogue']
    test_dialogue = Dialogue(dialogue=test_dialogue)
    test_graph = test_data['graph']
    test_graph = Graph(graph_dict=test_graph)


def run_all_algorithms():
    # Get all registered classes
    algorithms = AlgorithmRegistry.get_all()
    print('Classes to test:', *algorithms.keys(), sep='\n')
    total_metrics = {}
    for class_ in algorithms:
        class_instance = algorithms[class_]['type']()
        metrics = {}
        if algorithms[class_]['input_type'] is BaseGraph:
            result = class_instance.invoke(test_graph)
            metrics = {
                "all_paths_sampled": all_paths_sampled(test_graph, result[0]),
                "all_utterances_present": all_utterances_present(test_graph, result)
            }

        elif algorithms[class_]['input_type'] is list[Dialogue]:
            result = class_instance.invoke(test_dialogue)
        
        total_metrics[class_] = metrics

    return total_metrics


if __name__=="__main__":
    with open("dev_packages/chatsky_llm_autoconfig/chatsky_llm_autoconfig/autometrics/results/results.json") as f:
        old_data = json.load(f)
    
    new_metrics = {str(datetime.datetime.now()): run_all_algorithms()}

    old_data.update(new_metrics)    

    with open("dev_packages/chatsky_llm_autoconfig/chatsky_llm_autoconfig/autometrics/results/results.json", 'w') as f:
        f.write(json.dumps(old_data, indent=2, ensure_ascii=False))