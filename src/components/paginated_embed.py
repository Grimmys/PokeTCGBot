import math
from typing import Optional, Callable, Sequence

from discord import Embed, Interaction, User, File
from discord.ui import Button, View


class PaginatedEmbed:
    t: Optional[Callable] = None

    @staticmethod
    def setup_class(get_localized_string_method: Callable):
        PaginatedEmbed.t = get_localized_string_method

    def __init__(self, original_interaction: Interaction, content: Sequence[dict[str, any]], image_mode: bool,
                 user_language_id: int, page_size: int = 1, inline: bool = False, title: str = None,
                 discord_user: User = None) -> None:
        self.user_language_id = user_language_id
        self.current_page = 0
        self.embed = Embed()
        if title is not None:
            self.embed.title = title
        if discord_user is not None:
            self.embed.set_author(name=discord_user.display_name, icon_url=discord_user.display_avatar.url)
        self.original_interaction = original_interaction
        self.content = content
        self.image_mode = image_mode
        self.attachments: list[File] = []
        self.page_size = page_size if not image_mode else 1
        self.inline = inline
        self.display_list(content[:page_size])

        self.view = View()
        next_button = Button(emoji="➡️")
        next_button.callback = lambda click_interaction: self.change_page(click_interaction, True)

        previous_button = Button(emoji="⬅️")
        previous_button.callback = lambda click_interaction: self.change_page(click_interaction, False)

        self.view.add_item(previous_button)
        self.view.add_item(next_button)

    async def change_page(self, click_interaction: Interaction, forward: bool):
        if click_interaction.user != self.original_interaction.user:
            return
        if forward:
            self.current_page += 1
        else:
            self.current_page -= 1
        if self.current_page * self.page_size >= len(self.content):
            self.current_page = 0
        elif self.current_page < 0:
            self.current_page = len(self.content) // self.page_size
            if self.current_page * self.page_size == len(self.content):
                self.current_page -= 1
        self.refresh_page()
        await self.original_interaction.edit_original_response(embed=self.embed, attachments=self.attachments)
        await click_interaction.response.defer()

    def refresh_page(self):
        self.embed.clear_fields()
        self.embed.set_image(url="")
        self.embed.set_footer(text="")
        displayed = self.content[self.current_page * self.page_size:(self.current_page + 1) * self.page_size]
        if len(displayed) == 0:
            self.embed.add_field(name=PaginatedEmbed.t(self.user_language_id, 'common.no_results'), value="")
        else:
            self.display_list(displayed)

    def display_list(self, displayed: Sequence[dict[str, any]]):
        self.attachments = []
        for element in displayed:
            self.embed.add_field(
                name=element["name"], value=element["value"], inline=self.inline)
            if self.image_mode:
                url = element["image"]
                if not url.startswith("http"):
                    self.attachments.append(File(f"assets/altered_cards/{element['image']}"))
                    url = f"attachment://{element['image']}"
                self.embed.set_image(url=url)
        footer_text = f'{self.current_page + 1}/{math.ceil(len(self.content) / self.page_size)}'
        if not self.image_mode:
            footer_text += f'   ({self.current_page * self.page_size + 1}-{min((self.current_page + 1) * self.page_size, len(self.content))}/{len(self.content)})'
        self.embed.set_footer(text=footer_text)
