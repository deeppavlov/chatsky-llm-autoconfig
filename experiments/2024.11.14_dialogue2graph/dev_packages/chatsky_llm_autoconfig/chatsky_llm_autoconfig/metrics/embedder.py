from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain.evaluation import load_evaluator
from chatsky_llm_autoconfig.utils import EnvSettings
env_settings = EnvSettings()
embedding_model = HuggingFaceEmbeddings(model_name=env_settings.EMBEDDER_MODEL, model_kwargs={"device": env_settings.EMBEDDER_DEVICE})
evaluator = load_evaluator("pairwise_embedding_distance", embeddings=embedding_model)

def compare_strings(first: str, second: str):

    score = evaluator.evaluate_string_pairs(prediction=first, prediction_b=second)['score']
    print("SCORE: ", score, first, second)
    return score <= env_settings.EMBEDDER_THRESHOLD

class EmbeddableString:
    def __init__(self, element: str):
        self.element = element
    def __eq__(self, other):
        return compare_strings(self.element,other.element)
    def __hash__(self):
        return hash("")
    def __str__(self):
        return self.element

def emb_list(x):
    #print("EMB_LIST: ", x, type(x))
    return [EmbeddableString(el) for el in x]