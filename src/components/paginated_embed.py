import math
from discord import Embed, User


class PaginatedEmbed:
    def __init__(self, content: list[dict[str, str]], image_mode: bool, page_size: int = 1, inline: bool = False, title: str = None, discord_user: User = None) -> None:
        self.current_page = 0
        self.embed = Embed()
        if title is not None:
            self.embed.title = title
        if discord_user is not None:
            self.embed.set_author(name=discord_user.display_name, icon_url=discord_user.display_avatar.url)
        self.content = content
        self.image_mode = image_mode
        self.page_size = page_size if not image_mode else 1
        self.inline = inline
        self.display_list(content[:page_size])

    def change_page(self, forward: bool):
        if forward:
            self.current_page += 1
        else:
            self.current_page -= 1
        if self.current_page * self.page_size >= len(self.content):
            self.current_page = 0
        elif self.current_page < 0:
            self.current_page = len(self.content) // self.page_size
            if (self.current_page * self.page_size == len(self.content)):
                self.current_page -= 1
        displayed = self.content[self.current_page * self.page_size:(self.current_page + 1) * self.page_size]
        self.embed.clear_fields()
        self.display_list(displayed)

    def display_list(self, displayed):
        for element in displayed:
            self.embed.add_field(
                name=element["name"], value=element["value"], inline=self.inline)
            if self.image_mode:
                self.embed.set_image(url=element["image"])
        footer_text = f'{self.current_page + 1}/{ math.ceil(len(self.content) / self.page_size) }'
        if not self.image_mode:
            footer_text += f'   ({self.current_page * self.page_size + 1}-{min((self.current_page + 1) * self.page_size, len(self.content))}/{len(self.content)})'
        self.embed.set_footer(text=footer_text)

