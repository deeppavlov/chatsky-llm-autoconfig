#from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.cross_encoders.huggingface import HuggingFaceCrossEncoder
from langchain.evaluation import load_evaluator
from chatsky_llm_autoconfig.utils import EnvSettings
env_settings = EnvSettings()
#embedding_model = HuggingFaceEmbeddings(model_name=env_settings.EMBEDDER_MODEL, model_kwargs={"device": env_settings.EMBEDDER_DEVICE})
#evaluator = load_evaluator("pairwise_embedding_distance", embeddings=embedding_model)

evaluator = HuggingFaceCrossEncoder(model_name=env_settings.RERANKER_MODEL, model_kwargs={"device": env_settings.EMBEDDER_DEVICE})

def compare_strings(first: str, second: str):

    # score = evaluator.evaluate_string_pairs(prediction=first, prediction_b=second)['score']
    score = evaluator.score([(first, second)])[0]
    if 0.99 > score > 0.94:
        print("SCORE: ", score, first, second)
    # return score <= env_settings.EMBEDDER_THRESHOLD
    return score >= env_settings.RERANKER_THRESHOLD

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
    #print("EMB_LIST: ", x)
    return [EmbeddableString(el) for el in x]

def get_embedding(golden: list[str], generated: list[str], emb_name: str, device: str):

    if emb_name not in embedding:
        embedding[emb_name] = SentenceTransformer(emb_name,device=device)
 
    golden_vectors = embedding[emb_name].encode(golden, normalize_embeddings=True)
    generated_vectors = embedding[emb_name].encode(generated, normalize_embeddings=True)
    similarities = generated_vectors @ golden_vectors.T
    return similarities