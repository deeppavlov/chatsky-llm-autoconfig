

from chatsky_llm_autoconfig.schemas import DialogueMessage
from langchain.prompts import PromptTemplate
from langchain_core.output_parsers import JsonOutputParser
from typing import List

from langchain_openai import ChatOpenAI
from pydantic import BaseModel

augmentation_prompt = PromptTemplate.from_template("""
You are tasked with augmenting a dialogue by adding variations to existing utterances while maintaining the original dialogue flow and intent.

THEME: {topic}

INPUT DIALOGUE:
{dialogue}

INSTRUCTIONS:
1. For each message in the dialogue:
   - Keep the same structure (participant, source, target if present)
   - Create variation of the 'text' field that:
     * Express the same meaning/intent
     * Use different wording and phrasing
     * Match the given theme
     * Sound natural and conversational

2. The output must be a list of dictionaries, where each dictionary has:
   - 'text': string
   - 'participant': either 'user' or 'assistant'
   
3. Ensure all utterance variations:
   - Are appropriate for the theme
   - Maintain consistency in tone and style
   - Make sense in the conversation flow

Return ONLY a valid JSON array containing the augmented dialogue messages. Each message should be in this exact format:
For assistant messages: {{"text": "utterance text", "participant": "assistant"}}
For user messages: {{"text": "utterance text", "participant": "user"}}

Example format:
[
    {{"text": "How may I assist you today?", "participant": "assistant"}},
    {{"text": "I need help with a package", "participant": "user"}},
    {{"text": "What kind of package is it?", "participant": "assistant"}}
]
""")


class DialogueSequence(BaseModel):
    result: List[DialogueMessage]


parser = JsonOutputParser(pydantic_object=DialogueSequence)

# Usage
model = ChatOpenAI(
    model="gpt-4o-mini",
    api_key=os.getenv("OPENAI_API_KEY"),
    base_url=os.getenv("OPENAI_BASE_URL"),
    temperature=0.7
)

chain = augmentation_prompt | model | parser


result = chain.invoke({
    "topic": topic,
    "dialogue": dialogue
})
