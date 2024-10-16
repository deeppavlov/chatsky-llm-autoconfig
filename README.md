# chatsky-llm-integration
Chatsky LLM-Autoconfig allows you to effortlessly create chatsky flows and scripts from dialogues using Large Language Models.

### Setup
```
poetry install
```

### Contents
```
./data - Examples, tests and other dialogue data in JSON format
./experiments - Test field for experimental features, test data and results
./metrics - Graph evaluation metrics module
./dev_packages/llm_autoconfig - Directory containing all the code for the `llm_autoconfig` module
```

### Current progress
Supported types of graphs:
  - [x]  chain
  - [x]  single cycle

Currently unsupported types:
  - [ ]  single node cycle
  - [ ]  multi-cycle graph
  - [ ]  incomplete graph
  - [ ]  complex graph with cycles


### Evaluation Pipeline:

After calculating the Jaccard index, we take all pairs of edge_i -> node -> edge_j, such that jaccard(edge_i, edge_j) > 0 and both edges are incident to the node.

The Triplet Match Accuracy is calculated.

Let's assume we have an ideal graph (ground truth).

To create a graph from scratch based on a dialogue, we attempt to construct a graph and compare it with a subgraph of the ideal graph that should have been obtained after building the graph from scratch using the dialogue. For all subsequent graphs, this task is already considered a graph completion task.

For the graph completion task, we take the graph that should have been obtained after construction based on the current dialogue and compare it with the one produced by the model.

## Prompts

### Graph creration prompt (one-shot): 

```
You have an example of dialogue from customer chatbot system. You also have an 
    example of set of rules how chatbot system works should be looking - it is 
    a set of nodes when chatbot system respons and a set of transitions that are 
    triggered by user requests. 
    Here is the example of set of rules: 
    'edges': [ [ 'source': 1, 'target': 2, 'utterances': 'I need to make an order' ], 
    [ 'source': 1, 'target': 2, 'utterances': 'I want to order from you' ], 
    [ 'source': 2, 'target': 3, 'utterances': 'I would like to purchase 'Pale Fire' and 'Anna Karenina', please' ], 
    'nodes': [ [ 'id': 1, 'label': 'start', 'is_start': true, 'utterances': [ 'How can I help?', 'Hello' ], 
    [ 'id': 2, 'label': 'ask_books', 'is_start': false, 'utterances': [ 'What books do you like?'] ] 
    I will give a dialogue, your task is to build a graph for this dialogue in the format above. We allow several edges with equal 
    source and target and also multiple responses on one node so try not to add new nodes if it is logical just to extend an 
    exsiting one. utterances in one node or on multiedge should close between each other and correspond to different answers 
    to one question or different ways to say something. For example, for question about preferences or a Yes/No question 
    both answers can be fit in one multiedge, there’s no need to make a new node. If two nodes has the same responses they 
    should be united in one node. Do not make up utterances that aren’t present in the dialogue. Please do not combine 
    utterances for multiedges in one list, write them separately like in example above. Every utterance from the dialogue, 
    whether it is from user or assistanst, should contain in one of the nodes. Edges must be utterances from the user. Do not forget ending nodes with goodbyes. 
    Sometimes dialogue can correspond to several iterations of loop, for example: 
    ['text': 'Do you have apples?', 'participant': 'user'], 
    ['text': 'Yes, add it to your cart?', 'participant': 'assistant'], 
    ['text': 'No', 'participant': 'user'], 
    ['text': 'Okay. Anything else?', 'participant': 'assistant'], 
    ['text': 'I need a pack of chips', 'participant': 'user'], 
    ['text': 'Yes, add it to your cart?', 'participant': 'assistant'], 
    ['text': 'Yes', 'participant': 'user'], 
    ['text': 'Done. Anything else?', 'participant': 'assistant'], 
    ['text': 'No, that’s all', 'participant': 'user'], 
    it corresponds to following graph: 
    [ nodes: 
    'id': 1, 
    'label': 'confirm_availability_and_ask_to_add', 
    'is_start': false, 
    'utterances': 'Yes, add it to your cart?' 
    ], 
    [ 
    'id': 2, 
    'label': 'reply_to_yes', 
    'is_start': false, 
    'utterances': ['Done. Anything else?', 'Okay. Anything else?'] 
    ], 
    [ 
    'id': 3, 
    'label': 'finish_filling_cart', 
    'is_start': false, 
    'utterances': 'Okay, everything is done, you can go to cart and finish the order.' 
    ], 
    edges: 
    [ 
    'source': 1, 
    'target': 2, 
    'utterances': 'Yes' 
    ], 
    [ 
    'source': 1, 
    'target': 2, 
    'utterances': 'No' 
    ], 
    [ 
    'source': 2, 
    'target': 1, 
    'utterances': 'I need a pack of chips' 
    ], 
    [ 
    'source': 2, 
    'target': 3, 
    'utterances': 'No, that’s all' 
    ]. 
    We encourage you to use cycles and complex interwining structure of the graph with 'Yes'/'No' edges for the branching.
    This is the end of the example. Brackets must be changed back into curly braces to create a valid JSON string. Return ONLY JSON string in plain text (no code blocks) without any additional commentaries.
    Dialogue: {dialog}
```

### Prompt for node/edge - utterance correspondance

```
You have a dialogue and a structure of graph built on this dialogue it is a set of nodes when chatbot system responses and a set of transitions that are triggered by user requests. 
Please say if for every utterance in the dialogue there exist either a utteranse in node or in some edge. be attentive to what nodes we actually have in the "nodes" list, because some nodes from the list of edges maybe non existent:
Graph: 
Dialogue:
just print the list of utteance and whether there exsit a valid edge of node contating it, if contains print the node or edge
```
### Graph validation prompt:

```
1. You have an example of dialogue from customer chatbot system.
2. You also have a set of rules how chatbot system works - a set of nodes when chatbot system respons and a set of transitions that are triggered by user requests.
3. Chatbot system can move only along transitions listed in 2.  If a transition from node A to node B is not listed we cannot move along it.
4. If a dialog doesn't contradcit with the rules listed in 2 print YES otherwise if such dialog could'nt happen because it contradicts the rules print NO. Dialogue: {dialogue}. Set of rules: {rules}
```
