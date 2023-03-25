import uuid


class SuggestionEntity:
    def __init__(self, author: str, content: str, suggestion_id: str = None,
                 up_votes: set[int] = None, down_votes: set[int] = None):
        self.id: str = str(uuid.uuid4()) if suggestion_id is None else suggestion_id
        self.author: str = author
        self.content: str = content
        self.up_votes: set[int] = up_votes if up_votes is not None else set()
        self.down_votes: set[int] = down_votes if down_votes is not None else set()

    def count_up_votes(self):
        return len(self.up_votes)

    def count_down_votes(self):
        return len(self.down_votes)

    def __setstate__(self, state):
        self.id = state.get("id", str(uuid.uuid4()))
        self.author = state.get("author")
        self.content = state.get("content")
        self.up_votes = state.get("up_votes", set())
        self.down_votes = state.get("down_votes", set())
