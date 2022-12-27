from discord import Embed


class PaginatedEmbed():
    def __init__(self, content: list[dict[str, str]], page_size: int = 1, inline: bool = False) -> None:
        self.current_page = 0
        self.embed = Embed()
        self.content = content
        self.page_size = page_size
        self.inline = inline
        for element in content[:page_size]:
            self.embed.add_field(
                name=element["name"], value=element["value"], inline=self.inline)

    def change_page(self, forward: bool):
        if forward:
            self.current_page += 1
        else:
            self.current_page -= 1
        if self.current_page * self.page_size > len(self.content):
            self.current_page = 0
        elif self.current_page < 0:
            self.current_page = len(self.content) // self.page_size
        displayed = self.content[self.current_page * self.page_size:(self.current_page + 1) * self.page_size]
        self.embed.clear_fields()
        for element in displayed:
            self.embed.add_field(
                name=element["name"], value=element["value"], inline=self.inline)
