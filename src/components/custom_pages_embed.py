from typing import Sequence, Callable

import discord
from discord import Interaction, User, Embed
from discord.ui import View, Button

from src.colors import BLACK


class Field:
    def __init__(self, name, value, inline=True):
        self.name = name
        self.value = value
        self.inline = inline


class Page:
    def __init__(self, button_emoji, title, fields: Sequence[Field], disable_check: Callable = None):
        self.button_emoji = button_emoji
        self.disable_check = disable_check if disable_check is not None else lambda: False
        self.title = title
        self.fields = fields

    def open_page(self, embed: Embed):
        embed.title = self.title
        embed.clear_fields()
        for field in self.fields:
            embed.add_field(name=field.name, value=field.value, inline=field.inline)

    async def open_page_on_click(self, click_interaction: discord.Interaction,
                                 original_interaction: discord.Interaction, embed: Embed):
        self.open_page(embed)

        await click_interaction.response.defer()
        await original_interaction.edit_original_response(embed=embed)


class CustomPagesEmbed:
    def __init__(self, original_interaction: Interaction, pages: Sequence[Page], discord_user: User,
                 color: int = BLACK) -> None:
        self.original_interaction = original_interaction
        self.user = discord_user
        self.current_page = 0
        self.pages = pages

        self.embed = Embed(color=color)
        self.embed.set_author(name=discord_user.display_name, icon_url=discord_user.display_avatar.url)
        self.pages[self.current_page].open_page(self.embed)

        self.view = View()
        for page in self.pages:
            page_button = Button()
            page_button.emoji = page.button_emoji
            page_button.disabled = page.disable_check()
            page_button.callback = lambda interaction, related_page = page: related_page.open_page_on_click(interaction,
                                                                            self.original_interaction, self.embed)
            self.view.add_item(page_button)
