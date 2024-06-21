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

### Таблица метрик 
[Таблица с метриками](./metrics.csv)

### Подсчет метрик:
У ассистента мы игнорируем source_target поля 


### Промпт для проверки:

1. You have an example of dialogue from customer chatbot system.
2. You also have a set of rules how chatbot system works - a set of nodes when chatbot system respons and a set of transitions that are triggered by user requests.
3. Chatbot system can move only along transitions listed in 2.  If a transition from node A to node B is not listed we cannot move along it.
4. If a dialog doesn't contradcit with the rules listed in 2 print YES otherwise if such dialog could'nt happen because it contradicts the rules print NO. Dialogue: {dialogue}. Set of rules: {rules}

