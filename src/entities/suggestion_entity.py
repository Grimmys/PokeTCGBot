import uuid


class SuggestionEntity:
    def __init__(self, author: str, content: str):
        self.id: str = str(uuid.uuid4())
        self.author: str = author
        self.content: str = content

    def __setstate__(self, state):
        self.id = state.get("id", str(uuid.uuid4()))
        self.author = state.get("author")
        self.content = state.get("content")
