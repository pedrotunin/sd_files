import json

class Mensagem:
    def __init__(self, type: str, content: dict) -> None:
        self.type = type
        self.content = content

    @staticmethod
    def from_json(j: str) -> "Mensagem":
        j = json.loads(j)
        return Mensagem(j["type"], j["content"])
    
    def to_json(self) -> str:
        return json.dumps(self.__dict__)
