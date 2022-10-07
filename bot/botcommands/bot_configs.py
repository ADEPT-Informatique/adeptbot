import configs
from bot.botcommands.utils.validators import has_at_least_role
from bot.db.services import ConfigsService
from bot.util import AdeptBotException
from discord.ext import commands


class BotConfigsCog(commands.Cog):
    def __init__(self) -> None:
        self.configs_service = ConfigsService()

    @commands.command(name="getspamconfigs")
    @commands.guild_only()
    @has_at_least_role(configs.ADMIN_ROLE)
    async def get_spam_configs(self, ctx: commands.Context):
        sc = self.configs_service.find_or_create_spam_configs()

        await ctx.send(sc.__dict__)

    @commands.command(name="editspamconfig", aliases=["esc"])
    @commands.guild_only()
    @has_at_least_role(configs.ADMIN_ROLE)
    async def edit_spam_config(self, ctx: commands.Context, key: str, value: int):
        """
        Modifie la configuration du spam.

        Paramètres
        ----------
        key: str
            La clé de la configuration à modifier (repetition, mute_time)
        value: int
            La nouvelle valeur de la configuration
        """
        if value < 0:
            raise AdeptBotException("La valeur doit être de 0 ou superieur.")

        sc = self.configs_service.find_or_create_spam_configs()

        if not hasattr(sc, key):
            raise AdeptBotException(f"Le paramêtre {key} n'est pas valide. Veuillez choisir parmis les suivantes: {', '.join(sc.__dict__.keys())}")

        setattr(sc, key, value)

        self.configs_service.update_configs(sc)

        await ctx.send(f"La valeur pour `{key}` est maintenant à `{value}`")
