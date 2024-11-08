from pydantic import BaseModel
from typing import Union
from chatsky_llm_autoconfig.algorithms import DialogueGenerator, DialogAugmentation, GraphGenerator


class Pipeline(BaseModel):
    steps: list[Union[DialogueGenerator, DialogAugmentation, GraphGenerator]]

    def _validate_pipeline(self):
        pass
