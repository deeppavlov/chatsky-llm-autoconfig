from chatsky_llm_autoconfig.algorithms.base import DialogAugmentation, DialogueGenerator, GraphGenerator
from pydantic import BaseModel
from typing import Union


class Pipeline(BaseModel):
    steps: list[Union[DialogueGenerator, DialogAugmentation, GraphGenerator]]

    def _validate_pipeline(self):
        pass
