class SuggestionEntity:
    def __init__(self, author: str, content: str):
        self.author: str = author
        self.content: str = content

    def __setstate__(self, state):
        self.author = state.get("author")
        self.content = state.get("content")
