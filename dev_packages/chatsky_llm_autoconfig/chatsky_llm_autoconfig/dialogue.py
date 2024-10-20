from pydantic import BaseModel
from typing import Optional, Any, Union
import json
import matplotlib.pyplot as plt
import abc
import logging

logger = logging.getLogger(__name__)


class Dialogue(BaseModel, abc.ABC):
    """
    Base class for all of the dialogues.

    Attributes
    ----------
    dialogue : list of dict
        A list containing dialogue entries, where each entry is a
        dictionary with "text" and "participant" keys.
        It is initialized with an empty dictionary.

    Examples
    --------
        Dialogue([{"text": "How can I help?", "participant": "assistant"}, {"text": "I need to make an order", "participant": "user"}])

    """

    dialogue: list[dict] = [{}]

    class Config:
        arbitrary_types_allowed = True

    def parse_string(self, string):
        self.dialogue = []
        for utt in string.split("\n"):
            participant, phrase = utt.split("\t")
            self.dialogue.append({"text": phrase, "participant": participant})

    def __str__(self):
        readable = "\n".join([utt["participant"] + ": " + utt["text"] for utt in self.dialogue])
        return readable.strip()
