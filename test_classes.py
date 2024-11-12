from chatsky_llm_autoconfig.algorithms.dialogue_generation import DialogueSampler
from chatsky_llm_autoconfig.dialogue import Dialogue
from chatsky_llm_autoconfig.graph import Graph
from chatsky_llm_autoconfig.metrics.automatic_metrics import all_paths_sampled
import json

with open('data/data.json', 'r') as f:
    data = json.load(f)

data = data[3]["target_graph"]

g = Graph(data)

dial_sampler = DialogueSampler()

dialogues = dial_sampler.invoke(graph=g, start_node=1)
print(all_paths_sampled(g, dialogues))
for i in dialogues:
    print(i, sep="\n----------\n")