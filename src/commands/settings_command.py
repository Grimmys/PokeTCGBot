import discord
from discord import SelectOption, Embed, app_commands
from discord.ext import commands
from discord.ui import View, Select

from src.entities.language_entity import LanguageEntity
from src.repositories.in_memory_settings_repository import InMemorySettingsRepository
from src.services.settings_service import SettingsService

supported_languages = [
    LanguageEntity(0, "Français", "🇫🇷", "Changer la langue en français"),
    LanguageEntity(1, "English", "🇬🇧", "Switch to English")
]
language_options = [SelectOption(label=language.label, value=str(language.id),
                                 emoji=language.emoji, description=language.description)
                    for language in supported_languages]

settings_service = SettingsService(InMemorySettingsRepository())


class SettingsCog(commands.Cog):
    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot

    @app_commands.command(name="settings", description="Change user settings")
    async def settings(self, interaction: discord.Interaction) -> None:
        embed = Embed(title="---------- Settings ----------", color=0x808080)
        embed.set_author(name=interaction.user.display_name, icon_url=interaction.user.display_avatar.url)

        current_user_language = supported_languages[settings_service.get_user_language_id(interaction.user.id)]
        language_field_id = 0
        embed.add_field(name="Language", value=f"{current_user_language.emoji} {current_user_language.label}",
                        inline=False)

        async def change_language_callback(language_interaction: discord.Interaction):
            selected_index = int(select.values[0])
            new_user_language = supported_languages[selected_index]
            settings_service.update_user_language(interaction.user.id, selected_index)
            embed.set_field_at(language_field_id, name=embed.fields[language_field_id].name,
                               value=f"{new_user_language.emoji} {new_user_language.label}",
                               inline=False)
            await language_interaction.response.edit_message(embed=embed, view=view)
            await language_interaction.response.send_message(
                f"Language changed to: {new_user_language.label}", delete_after=2)

        select = Select(
            placeholder="Change language",
            options=language_options
        )
        select.callback = change_language_callback

        view = View()
        view.add_item(select)

        await interaction.response.send_message(embed=embed, view=view)
