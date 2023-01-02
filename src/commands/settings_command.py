import discord
from discord import SelectOption, Embed, app_commands
from discord.ext import commands
from discord.ui import View, Select

from src.colors import GRAY
from src.services.localization_service import LocalizationService
from src.services.settings_service import SettingsService

language_options = [SelectOption(label=language.label, value=str(language.id),
                                 emoji=language.emoji, description=language.description)
                    for language in LocalizationService.supported_languages]


class SettingsCog(commands.Cog):
    def __init__(self, bot: commands.Bot, settings_service: SettingsService,
                 localization_service: LocalizationService) -> None:
        self.bot = bot
        self.settings_service = settings_service
        self.t = localization_service.get_string

    @app_commands.command(name="settings", description="Change user settings")
    async def settings_command(self, interaction: discord.Interaction) -> None:
        user_language_id = self.settings_service.get_user_language_id(interaction.user.id)

        embed = Embed(
            title=f"---------- {self.t(user_language_id, 'settings_cmd.title')} ----------",
            color=GRAY)
        embed.set_author(name=interaction.user.display_name, icon_url=interaction.user.display_avatar.url)

        current_user_language = LocalizationService.supported_languages[user_language_id]

        language_field_id = 0
        embed.add_field(name=self.t(user_language_id, 'settings_cmd.language_field_name'),
                        value=f"{current_user_language.emoji} {current_user_language.label}",
                        inline=False)

        async def change_language_callback(language_interaction: discord.Interaction):
            if language_interaction.user != interaction.user:
                return

            selected_index = int(select.values[0])
            new_user_language = LocalizationService.supported_languages[selected_index]

            self.settings_service.update_user_language(interaction.user.id, selected_index)

            embed.set_field_at(language_field_id, name=embed.fields[language_field_id].name,
                               value=f"{new_user_language.emoji} {new_user_language.label}",
                               inline=False)
            await interaction.edit_original_response(embed=embed, view=view)
            await language_interaction.response.send_message(
                f"{self.t(new_user_language.id, 'settings_cmd.language_changed_response_msg')} {new_user_language.label}",
                delete_after=2)

        select = Select(
            placeholder=self.t(user_language_id, 'settings_cmd.select_language_placeholder'),
            options=language_options
        )
        select.callback = change_language_callback

        view = View()
        view.add_item(select)

        await interaction.response.send_message(embed=embed, view=view)
