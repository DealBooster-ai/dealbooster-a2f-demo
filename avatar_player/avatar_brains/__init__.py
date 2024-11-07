from abc import abstractmethod
import dataclasses
from typing import Any, List
import json

@dataclasses.dataclass
class Phrase:
    text: str
    emotion: str

class EnhancedJSONEncoder(json.JSONEncoder):
    def default(self, o):
        if dataclasses.is_dataclass(o):
            return dataclasses.asdict(o)
        return super().default(o)

@dataclasses.dataclass
class Utterance:
    role: str
    name: str
    phrases: List[Phrase]

    def text(self) -> str:
        result = ""
        for p in self.phrases:
            result = result + p.text
        return result
    
    def set_text(self, text:str):
        self.phrases = [Phrase(text, "normal")]

class IAvatarBrians():

    message_history: list

    def __init__(self):
        self.message_history = list()
    
    @abstractmethod
    def generate_reply(self, user_utterance):
        yield user_utterance
    
    def clear_history(self):
        self.message_history = list()




