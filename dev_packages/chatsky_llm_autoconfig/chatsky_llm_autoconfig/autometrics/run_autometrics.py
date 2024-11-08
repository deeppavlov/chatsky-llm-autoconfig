from chatsky_llm_autoconfig.autometrics.registry import AlgorithmRegistry
import chatsky_llm_autoconfig.algorithms.dialogue_generation
import chatsky_llm_autoconfig.algorithms.dialogue_augmentation
import chatsky_llm_autoconfig.algorithms.graph_generation

import json
from chatsky_llm_autoconfig.graph import Graph, BaseGraph
from chatsky_llm_autoconfig.dialogue import Dialogue
from chatsky_llm_autoconfig.metrics.automatic_metrics import *
import datetime


with open("dev_packages/chatsky_llm_autoconfig/chatsky_llm_autoconfig/autometrics/test_data/data.json") as f:
    test_data = json.load(f)
    graph_to_dialogue = test_data["graph_to_dialogue"]
    dialogue_to_dialogue = test_data["dialogue_to_dialogue"]

def run_all_algorithms():
    # Get all registered classes
    algorithms = AlgorithmRegistry.get_all()
    print("Classes to test:", *algorithms.keys(), sep="\n")
    total_metrics = {}
    for class_ in algorithms:
        class_instance = algorithms[class_]["type"]()
        metrics = {}

        if algorithms[class_]["input_type"] is BaseGraph and algorithms[class_]["output_type"] is Dialogue:
            metrics = {
                    "all_paths_sampled": [],
                    "all_utterances_present": [],
                }
            for case in graph_to_dialogue:
                test_dialogue = Dialogue(dialogue=case["dialogue"])
                test_graph = Graph(graph_dict=case["graph"])
                result = class_instance.invoke(test_graph)
                
                metrics["all_paths_sampled"].append(all_paths_sampled(test_graph, result[0]))
                metrics["all_utterances_present"].append(all_utterances_present(test_graph, result))
            
            metrics["all_paths_sampled_avg"] = sum(metrics["all_paths_sampled"])/len(metrics["all_paths_sampled"])
            metrics["all_utterances_present_avg"] = sum(metrics["all_utterances_present"])/len(metrics["all_utterances_present"])

        elif algorithms[class_]["input_type"] is Dialogue and algorithms[class_]["output_type"] is Dialogue:
            metrics = {
                "all_roles_correct": [],
                "is_correct_lenght": [],
            }
            for case in dialogue_to_dialogue:
                test_dialogue = Dialogue(dialogue=case["dialogue"])
                result = class_instance.invoke(test_dialogue)

                metrics["all_roles_correct"].append(all_roles_correct(test_dialogue, result))
                metrics["is_correct_lenght"].append(is_correct_lenght(test_dialogue, result))
            
            metrics["all_roles_correct_avg"] = sum(metrics["all_roles_correct"])/len(metrics["all_roles_correct"])
            metrics["is_correct_lenght_avg"] = sum(metrics["is_correct_lenght"])/len(metrics["is_correct_lenght"])
        
        elif algorithms[class_]["input_type"] is str and algorithms[class_]["output_type"] is BaseGraph:
            result = class_instance.invoke(test_dialogue)
            metrics = {
                
            }

        total_metrics[class_] = metrics

    return total_metrics

def compare_results(date, old_data):

    current_metrics = old_data.get(date, {})
    previous_date = list(old_data.keys())[-2]
    previous_metrics = old_data.get(previous_date, {})

    differences = {}
    for algorithm, metrics in current_metrics.items():
        if algorithm in previous_metrics:
            differences[algorithm] = {
                "all_paths_sampled_diff": metrics.get("all_paths_sampled_avg", 0) - previous_metrics[algorithm].get("all_paths_sampled_avg", 0),
                "all_utterances_present_diff": metrics.get("all_utterances_present_avg", 0) - previous_metrics[algorithm].get("all_utterances_present_avg", 0),
                "all_roles_correct_diff": metrics.get("all_roles_correct_avg", 0) - previous_metrics[algorithm].get("all_roles_correct_avg", 0),
                "is_correct_length_diff": metrics.get("is_correct_lenght_avg", 0) - previous_metrics[algorithm].get("is_correct_lenght_avg", 0),
                "total_diff": (
                    metrics.get("all_paths_sampled_avg", 0) +
                    metrics.get("all_utterances_present_avg", 0) +
                    metrics.get("all_roles_correct_avg", 0) +
                    metrics.get("is_correct_lenght_avg", 0)
                ) - (
                    previous_metrics[algorithm].get("all_paths_sampled_avg", 0) +
                    previous_metrics[algorithm].get("all_utterances_present_avg", 0) +
                    previous_metrics[algorithm].get("all_roles_correct_avg", 0) +
                    previous_metrics[algorithm].get("is_correct_lenght_avg", 0)
                )
            }

    return differences


if __name__ == "__main__":
    with open("dev_packages/chatsky_llm_autoconfig/chatsky_llm_autoconfig/autometrics/results/results.json") as f:
        old_data = json.load(f)

    date = str(datetime.datetime.now())
    new_metrics = {date: run_all_algorithms()}
    old_data.update(new_metrics)
    print(compare_results(date, old_data))

    with open("dev_packages/chatsky_llm_autoconfig/chatsky_llm_autoconfig/autometrics/results/results.json", "w") as f:
        f.write(json.dumps(old_data, indent=2, ensure_ascii=False))
