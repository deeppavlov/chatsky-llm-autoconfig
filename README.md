# dff-llm-integration

### Типы графов

  - [x]  зацикленная нода
  - [x]  цепочка
  - [x]  один цикл
  - [x]  несколько циклов
  - [x]  неполный граф - из цикла

### Файлы:

1. [Примеры диалогов-цепочек](./examples_of_dialogues.json)
2. [Файл с примерами реплик и нод для различных типов](./types_of_dialogues.json)
3. [Сэмплированные диалоги с помощью gpt-4o](./sampled_dialogues.json)
4. [Восстановленные пути с помощью gpt-4o](./remade_dialogue_routes.json)


### Подсчет метрик:
У ассистента мы игнорируем source_target поля 


### Промпт для проверки:

1. You have an example of dialogue from customer chatbot system.
2. You also have a set of rules how chatbot system works - a set of nodes when chatbot system respons and a set of transitions that are triggered by user requests.
3. Chatbot system can move only along transitions listed in 2.  If a transition from node A to node B is not listed we cannot move along it.
4. If a dialog doesn't contradcit with the rules listed in 2 print YES otherwise if such dialog could'nt happen because it contradicts the rules print NO. Dialogue: {dialogue}. Set of rules: {rules}

### Пример добавления ноды:
Sure, let's expand the set of rules to accommodate the new dialogue. We need to create new nodes and links to handle the request to change the payment method. Here is the updated set of rules:

### Nodes
```json
[
    {
        "id": 1,
        "label": "start",
        "is_start": true,
        "response": "Is there anything can I help with?"
    },
    {
        "id": 6,
        "label": "change_info",
        "is_start": false,
        "response": "Sure, what would you like to change?"
    },
    {
        "id": 7,
        "label": "change_payment_method",
        "is_start": false,
        "response": "Okay, it's changed!"
    },
    {
        "id": 9,
        "label": "add_books",
        "is_start": false,
        "response": "Done, this is added to your order!"
    },
    {
        "id": 10,
        "label": "confirm",
        "is_start": false,
        "response": "Done!"
    }
]
```

### Links
```json
[
    {
        "source": 1,
        "target": 6,
        "request": "I would like to change the information about my order number 33543"
    },
    {
        "source": 1,
        "target": 6,
        "request": "I would like to change the information about my order number 234"
    },
    {
        "source": 6,
        "target": 9,
        "request": "I want to add a book 'Cather in the Rye'"
    },
    {
        "source": 6,
        "target": 7,
        "request": "I would like to change payment method from cash to card"
    },
    {
        "source": 9,
        "target": 10,
        "request": "Thank you, that's all"
    }
]
```

### Updated Dialogue
Here is how the new dialogue fits into the updated set of rules:

```json
[
    {"text": "Is there anything can I help with?", "participant": "assistant"},
    {"text": "I would like to change the information about my order number 234", "participant": "user"},
    {"text": "Sure, what would you like to change?", "participant": "assistant"},
    {"text": "I would like to change payment method from cash to card", "participant": "user"},
    {"text": "Okay, it's changed!", "participant": "assistant"},
    {"text": "Good, thanks", "participant": "user"}
]
```

By adding the new node "change_payment_method" and the corresponding link from "change_info" to "change_payment_method", we ensure that the dialogue is now valid within the chatbot system's set of rules.
