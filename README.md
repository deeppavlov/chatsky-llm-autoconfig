# dff-llm-integration
### Добавление src package
```
pip install -e .
```

### Примеры графов

  - [x]  зацикленная нода (dataset/graphs.json -> 1)
  - [x]  цепочка  (dataset/graphs.json -> 2)
  - [x]  один цикл  (dataset/graphs.json -> 3)
  - [x]  несколько циклов  (dataset/graphs.json -> 4)
  - [x]  неполный граф - из цикла (dataset/graphs.json -> 5)
  - [x]  большой сложный граф из циклов (dataset/graphs.json -> 6)

### Файлы:

1. [Примеры диалогов-цепочек](./examples_of_dialogues.json)
2. [Файл с примерами реплик и нод для различных типов](./dataset/graphs.json)
3. [Сэмплированные диалоги из графов в (2) с помощью gpt-4o](./dataset/dialogues.json)

### Таблица метрик 
[Таблица с метриками](./metrics.csv)

### Подсчет метрик:

После подчета Жаккара мы берем все пары edge_i -> node -> edge_j, так что jaccard(edge_i, edge_j) > 0 и оба ребра инциденты ноде node.

Подсчитывается Triplet Match Accuracy.

Пусть у нас есть идельный граф (ground_truth).

Для создания графа с нуля по диалогу пытается построиться граф и мы его сравниваем с подграфом идеального графа, который должен бы был получиться после простроения графа с нуля по диалогу. Для всех следующих графов данная задача уже является задачей достраивания графа.

Для задачи достраивания графа мы берем граф, который должен бы получиться после построения на текущем диалоге и сравниваем его с тем, который получился у модели.

# Промпты

## Промпт для создания графа с нуля: 

You have an example of dialogue from customer chatbot system. You also have a example of set of rules how chatbot system works should be looking - it is a set of nodes when chatbot system respons and a set of transitions that are triggered by user requests. 
Here is the example of set of rules: 
"edges": [ { "source": 1, "target": 2, "utterances": "I need to make an order" },
 { "source": 1, "target": 2, "utterances": "I want to order from you" }, 
{ "source": 2, "target": 3, "utterances": "I would like to purchase 'Pale Fire' and 'Anna Karenina', please" }, 
"nodes": [ { "id": 1, "label": "start", "is_start": true, "utterances": [ "How can I help?", "Hello" ], 
{ "id": 2, "label": "ask_books", "is_start": false, "utterances": [ "What books do you like?"], }

I will give a dialogue, your task is to build a graph for this dialogue in the format above. We allow several edges with equal soruce and target and also multiple respnses on one node so try not to add new nodes if it is logical just to extend an exsiting one. utterances in one node or on multiedge should close between each other and correspond to different answers to one question or different ways to say something.  For example, for question about preferences or a Yes/No question both answers can be fit in one multiedge, there's no need to make a new node.  If two nodes has the same responses they should be united in one node. Do not make up utterances that aren't present in the dialogue. Please do not combine utterances for multiedges in one list, write them separately like in example above. Every utterance from the dialogue, whether it is from user or assistanst, should contain in one of the nodes. Do not forget ending nodes with goodbyes. 

Sometimes dialogue can correspond to several iterations of loop, for example:
  {"text": "Do you have apples?, "participant": "user"},
        {"text": "Yes,  add it to your cart?", "participant": "assistant»},
        {"text": "No", "participant": "user"},
        {"text": "Okay. Anything else?", "participant": "assistant"},
        {"text": "I need a pack of chips, "participant": "user"},
        {"text": "Yes,  add it to your cart?, "participant": "assistant"},
        {"text": "Yes", "participant": "user"},
        {"text": "Done. Anything else?", "participant": "assistant"},
        {"text": "No, that's all", "participant": "user"},

it corresponds to following graph:
{ nodes: 
            "id": 1,
            "label": "confirm_availability_and_ask_to_add",
            "is_start": false,
            "utterances": "Yes,  add it to your cart?"
        },
        {
            "id": 2,
            "label": "reply_to_yes",
            "is_start": false,
            "utterances": ["Done. Anything else?", "Okay. Anything else?"]
        },
        {
            "id»:3,
            "label": "finish_filling_cart",
            "is_start": false,
            "utterances": "Okay, everything is done, you can go to cart and finish the order."
        },

edges:
 {
            "source": 1,
            "target": 2,
            "utterances": "Yes"
        },
        {
            "source": 1,
            "target": 2,
            "utterances": "No"
        },
        {
            "source": 2,
            "target": 1,
            "utterances": "I need a pack of chips"
        },
        {
            "source": 2,
            "target": 3,
            "utterances": "No, that's all"
        }.      
This is the end of the example. 
Dialogue: 

## Промпт для проверки, что каждой реплике соответствует какая-то нода / ребро

You have a dialogue and a structure of graph built on this dialogue it is a set of nodes when chatbot system responses and a set of transitions that are triggered by user requests. 
Please say if for every utterance in the dialogue there exist either a utteranse in node or in some edge. be attentive to what nodes we actually have in the "nodes" list, because some nodes from the list of edges maybe non existent:
Graph: 
Dialogue:
just print the list of utteance and whether there exsit a valid edge of node contating it, if contains print the node or edge

## Промпт для проверки что граф валидный:

1. You have an example of dialogue from customer chatbot system.
2. You also have a set of rules how chatbot system works - a set of nodes when chatbot system respons and a set of transitions that are triggered by user requests.
3. Chatbot system can move only along transitions listed in 2.  If a transition from node A to node B is not listed we cannot move along it.
4. If a dialog doesn't contradcit with the rules listed in 2 print YES otherwise if such dialog could'nt happen because it contradicts the rules print NO. Dialogue: {dialogue}. Set of rules: {rules}

