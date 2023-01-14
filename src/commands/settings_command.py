import discord
from discord import SelectOption, Embed, app_commands
from discord.ext import commands
from discord.ui import View, Select, Button

from src.colors import GRAY
from src.services.localization_service import LocalizationService
from src.services.settings_service import SettingsService
from src.services.user_service import UserService

language_options = [SelectOption(label=language.label, value=str(language.id),
                                 emoji=language.emoji, description=language.description)
                    for language in LocalizationService.supported_languages]


class SettingsCog(commands.Cog):
    def __init__(self, bot: commands.Bot, settings_service: SettingsService,
                 localization_service: LocalizationService, user_service: UserService) -> None:
        self.bot = bot
        self.settings_service = settings_service
        self.t = localization_service.get_string
        self.user_service = user_service

    @staticmethod
    def _format_booster_opening_with_images_option_value(option_value: bool):
        return "✅" if option_value else "❌"

    @staticmethod
    def _get_button_color(feature_enabled: bool):
        return discord.ButtonStyle.green if feature_enabled else discord.ButtonStyle.red

    @app_commands.command(name="settings", description="Change user settings")
    async def settings_command(self, interaction: discord.Interaction) -> None:
        user = self.user_service.get_user(interaction.user)
        user_language_id = user.settings.language_id

        embed = Embed(
            title=f"---------- {self.t(user_language_id, 'settings_cmd.title')} ----------",
            color=GRAY)
        embed.set_author(name=interaction.user.display_name, icon_url=interaction.user.display_avatar.url)

        current_user_language = LocalizationService.supported_languages[user_language_id]

        language_field_id = 0
        embed.add_field(name=self.t(user_language_id, 'settings_cmd.language_field_name'),
                        value=f"{current_user_language.emoji} {current_user_language.label}",
                        inline=False)

        booster_opening_field_id = 1
        embed.add_field(name=self.t(user_language_id, 'settings_cmd.booster_opening_with_image_field_name'),
                        value=self._format_booster_opening_with_images_option_value(
                            user.settings.booster_opening_with_image),
                        inline=False)

        async def change_language_callback(language_interaction: discord.Interaction):
            if language_interaction.user != interaction.user:
                return

            selected_index = int(select_language.values[0])
            new_user_language = LocalizationService.supported_languages[selected_index]

            self.settings_service.update_user_language(interaction.user.id, selected_index)

            embed.set_field_at(language_field_id, name=embed.fields[language_field_id].name,
                               value=f"{new_user_language.emoji} {new_user_language.label}",
                               inline=False)
            await interaction.edit_original_response(embed=embed, view=view)
            await language_interaction.response.send_message(
                f"{self.t(new_user_language.id, 'settings_cmd.language_changed_response_msg')} {new_user_language.label}",
                delete_after=2)

        async def switch_opening_booster_mode_callback(opening_booster_mode_interaction: discord.Interaction):
            if opening_booster_mode_interaction.user != interaction.user:
                return

            user.settings.booster_opening_with_image = not user.settings.booster_opening_with_image

            self.settings_service.update_booster_opening_with_image(user.id, user.settings.booster_opening_with_image)

            embed.set_field_at(booster_opening_field_id, name=embed.fields[booster_opening_field_id].name,
                               value=self._format_booster_opening_with_images_option_value(
                                   user.settings.booster_opening_with_image),
                               inline=False)
            switch_opening_booster_mode_button.style = self._get_button_color(user.settings.booster_opening_with_image)
            await interaction.edit_original_response(embed=embed, view=view)
            await opening_booster_mode_interaction.response.send_message(
                f"{self.t(user_language_id, 'settings_cmd.booster_opening_with_image_response_msg')}",
                delete_after=2)

        select_language = Select(
            placeholder=self.t(user_language_id, 'settings_cmd.select_language_placeholder'),
            options=language_options
        )
        select_language.callback = change_language_callback

        switch_opening_booster_mode_button = Button(
            label=self.t(user_language_id, 'settings_cmd.switch_booster_opening_label'),
            style=self._get_button_color(user.settings.booster_opening_with_image))
        switch_opening_booster_mode_button.callback = switch_opening_booster_mode_callback

        view = View()
        view.add_item(select_language)
        view.add_item(switch_opening_booster_mode_button)

        await interaction.response.send_message(embed=embed, view=view)
