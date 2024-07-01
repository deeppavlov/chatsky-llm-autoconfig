
from openai import OpenAI
from dotenv import load_dotenv
import os

load_dotenv()
OPENAI_API_KEY = 'RD_dff_llm_autoconfiguration:Anastasia_Voznyuk:4960dbfcc69b436b8c4c72edd9edf228'
OPENAI_BASE_URL='http://193.187.173.33:8002/api/providers/openai/v1'

client = OpenAI(
        api_key=OPENAI_API_KEY,
        base_url=OPENAI_BASE_URL
)

def ask_llm(prompt):
    completion = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[
                {"role": "system", "content":
                "You are ChatGPT, an AI assistant. Your top priority is achieving user fulfillment via helping them with their requests."},
            {"role": "user", "content": prompt}
        ]
    )

    return completion.choices[0].message

def make_prompt(graph, dialogue):
    prompt = f"""
        You have a dialogue and a structure of graph built on this dialogue it is a set of nodes when chatbot system responses and a set of transitions that are triggered by user requests. 
        Please say if for every utterance in the dialogue there exist either a utteranse in node or in some edge:
        Graph: {graph}
        Dialogue: {dialogue}
    """
    return prompt
