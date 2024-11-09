from typing import List, Union, Dict
from chatsky_llm_autoconfig.schemas import DialogueMessage
from pydantic import BaseModel, Field, ConfigDict


class Dialogue(BaseModel):
    """Represents a complete dialogue consisting of multiple messages.

    The class provides methods for creating dialogues from different formats
    and converting dialogues to various representations.
    """
    messages: List[DialogueMessage] = Field(default_factory=list)
    topic: str = ""

    model_config = ConfigDict(
        arbitrary_types_allowed=True,
        frozen=False,  # Dialogue needs to be mutable to append messages
    )

    @classmethod
    def from_string(cls, string: str) -> "Dialogue":
        """Creates a Dialogue from a tab-separated string format.

        Args:
            string: Tab-separated string with format: "participant\ttext\n"

        Returns:
            Dialogue object with parsed messages
        """
        messages: List[DialogueMessage] = [
            DialogueMessage(participant=line.split(
                "\t")[0], text=line.split("\t")[1])
            for line in string.strip().split("\n")
        ]
        return cls(messages=messages)

    @classmethod
    def from_list(cls, dialogue_list: List[Dict[str, str]]) -> "Dialogue":
        """Creates a Dialogue from a list of message dictionaries.

        Args:
            dialogue_list: List of dicts with 'text' and 'participant' keys

        Returns:
            Dialogue object with parsed messages
        """
        messages = [DialogueMessage(**msg) for msg in dialogue_list]
        return cls(messages=messages)

    def to_list(self) -> List[Dict[str, str]]:
        """Converts Dialogue to a list of message dictionaries."""
        return [msg.model_dump() for msg in self.messages]

    def __str__(self) -> str:
        """Returns a readable string representation of the dialogue."""
        return "\n".join(
            f"{msg.participant}: {msg.text}"
            for msg in self.messages
        ).strip()

    def append(self, text: str, participant: str) -> None:
        """Adds a new message to the dialogue.

        Args:
            text: Content of the message
            participant: Sender of the message
        """
        self.messages.append(DialogueMessage(
            text=text, participant=participant))

    def extend(self, messages: List[Union[DialogueMessage, Dict[str, str]]]) -> None:
        """Adds multiple messages to the dialogue.

        Args:
            messages: List of DialogueMessage objects or dicts to add
        """
        new_messages = [
            msg if isinstance(msg, DialogueMessage) else DialogueMessage(**msg)
            for msg in messages
        ]
        self.messages.extend(new_messages)


# Type-safe usage examples
if __name__ == "__main__":
    # Create from list of dicts
    dialogue1 = Dialogue(messages=[
        DialogueMessage(text="How can I help?", participant="assistant"),
        DialogueMessage(text="I need coffee", participant="user")
    ])

    # Create using from_list
    dialogue2 = Dialogue.from_list([
        {"text": "How can I help?", "participant": "assistant"},
        {"text": "I need coffee", "participant": "user"}
    ])

    # Create from string
    dialogue3 = Dialogue.from_string("""
        assistant\tHow can I help?
        user\tI need coffee
""".strip())

    # Append and extend
    dialogue1.append("What kind of coffee?", "assistant")
    dialogue1.extend([
        {"text": "Espresso please", "participant": "user"},
        DialogueMessage(text="Coming right up!", participant="assistant")
    ])
