"""Module for dynamic bot configurations."""

from discord.ext import commands

import configs
from bot.botcommands.utils.validators import has_at_least_role
from bot.db.services import ConfigsService
from bot.util import AdeptBotException


class BotConfigsCog(commands.Cog):
    """Cog pour les configurations dynamiques du bot"""

    def __init__(self) -> None:
        self.configs_service = ConfigsService()

    @commands.command(name="getspamconfigs")
    @commands.guild_only()
    @has_at_least_role(configs.ADMIN_ROLE)
    async def get_spam_configs(self, ctx: commands.Context):
        """Affiche la configuration du spam."""
        spam_config = self.configs_service.find_or_create_spam_configs()

        await ctx.send(spam_config.__dict__)

    @commands.command(name="editspamconfig", aliases=["esc"])
    @commands.guild_only()
    @has_at_least_role(configs.ADMIN_ROLE)
    async def edit_spam_config(self, ctx: commands.Context, key: str, value: int):
        """
        Modifie la configuration du spam.

        Utilisation:
        !editspamconfig repetition 10
        !editspamconfig mute_time 60
        """
        if value < 0:
            raise AdeptBotException("La valeur doit être de 0 ou superieur.")

        spam_config = self.configs_service.find_or_create_spam_configs()

        if key not in spam_config.__slots__:
            raise AdeptBotException(
                f"Le paramêtre {key} n'est pas valide. " +
                f"Veuillez choisir parmis les suivantes: {', '.join(spam_config.__slots__)}"
            )

        setattr(spam_config, key, value)

        self.configs_service.update_configs(spam_config)

        await ctx.send(f"La valeur pour `{key}` est maintenant à `{value}`")
