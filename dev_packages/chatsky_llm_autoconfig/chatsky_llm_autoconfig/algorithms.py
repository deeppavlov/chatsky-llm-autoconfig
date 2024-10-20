from pydantic import BaseModel
import abc
from chatsky_llm_autoconfig.graph import BaseGraph
from chatsky_llm_autoconfig.dialogue import Dialogue

class BaseAlgorithm(BaseModel, abc.ABC):
    
    @abc.abstractmethod
    def invoke(self, *args, **kwargs):
        raise NotImplementedError
    
    @abc.abstractmethod
    async def ainvoke(self, *args, **kwargs):
        raise NotImplementedError


class DialogueGenerator(BaseAlgorithm):
    
    def __init__(self):
        super().__init__()
    
    def invoke(self, graph: BaseGraph) -> Dialogue:
        raise NotImplementedError