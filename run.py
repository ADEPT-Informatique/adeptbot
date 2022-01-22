import asyncio
import disnake
import traceback
from disnake.ext import commands
from bot.botcommands import MemberCog, ModerationCog

import configs
from bot import tasks, util, welcome
from bot.interactions import TicketOpeningInteraction, TicketCloseInteraction
from bot.welcome import NoReplyException


class AdeptClient(commands.Bot):
    def __init__(self, prefix):
        intents = disnake.Intents.default()
        intents.members = True
        loop = asyncio.get_event_loop_policy().new_event_loop()
        super().__init__(prefix, loop=loop, intents=intents)

        self.add_cog(MemberCog(self))
        self.add_cog(ModerationCog(self))
        self.persistent_views_loaded = False

    async def on_ready(self):
        util._load(self)
        util.logger.info(f"\nLogged in with account @{self.user.name} ID:{self.user.id} \n------------------------------------\n")
        
        if not self.persistent_views_loaded:
            self.add_view(TicketOpeningInteraction())
            self.add_view(TicketCloseInteraction())
            self.persistent_views_loaded = True

        await self.change_presence(activity=disnake.Activity(name="for bad boys!", type=disnake.ActivityType.watching))
        tasks._load_tasks(self)

    async def on_message(self, message: disnake.Message):
        if (message.author.bot):
            return

        message.content = message.content.replace(f"<@!{self.user.id}>", configs.PREFIX, 1) if message.content.startswith(f"<@!{self.user.id}>") else message.content
        message.content = message.content.replace(f"<@{self.user.id}>", configs.PREFIX, 1) if message.content.startswith(f"<@{self.user.id}>") else message.content

        if message.content.startswith(configs.PREFIX):
            await self.process_commands(message)

    async def on_message_edit(self, before: disnake.Message, after: disnake.Message):
        if before.author.bot:
            return

        embed = disnake.Embed(title="Message édité", color=0x00ff00, timestamp=disnake.utils.utcnow(), url=after.jump_url)

        if before.content != after.content:
            embed.add_field(name="Contenu avant", value=before.content)
            embed.add_field(name="Contenu après", value=after.content, inline=False)

        if embed.fields:
            await self.say(configs.LOGS_CHANNEL, embed=embed)

    async def on_message_delete(self, message: disnake.Message):
        embed = disnake.Embed(title="Message supprimé", color=0xff0000, timestamp=disnake.utils.utcnow())
        embed.add_field(name="Contenu", value=message.content, inline=False)

        if message.author.id != self.user.id:
            logs = await message.guild.audit_logs(limit=1, action=disnake.AuditLogAction.message_delete).flatten()
            if logs:
                embed.add_field(name="Supprimé par", value=logs[0].user.mention, inline=False)
            else:
                embed.add_field(name="Supprimé par", value="Inconnu", inline=False)

        await self.say(configs.LOGS_CHANNEL, embed=embed)

    async def on_member_join(self, member: disnake.Member):
        await self.say(configs.LOGS_CHANNEL, f"{member.mention} a rejoint le serveur.")
        await self.change_presence(activity=disnake.Activity(name="for bad boys!", type=disnake.ActivityType.watching))
        tasks._load_tasks(self)

    async def on_member_join(self, member: disnake.Member):
        await self.say(configs.WELCOME_CHANNEL, configs.WELCOME_SERVER.format(name=member.mention))
        result = await welcome.walk_through_welcome(member)

        await welcome.process_welcome_result(member, result)

    async def on_member_remove(self, member: disnake.Member):
        await self.say(configs.LOGS_CHANNEL, f"{member.mention} a quitté le serveur.")

    async def on_member_update(self, before: disnake.Member, after: disnake.Member):
        embed = disnake.Embed(title="Membre modifié", color=0x00ff00)
        embed.add_field(name="Membre", value=f"{after.mention}")

        if before.nick != after.nick:
            embed.add_field(name="Nom", value=f"{before.mention} -> {after.mention}")
        
        if before.voice != after.voice:
            if before.voice is None:
                embed.add_field(name="Canal vocal", value=f"{before.mention} s'est connecté à {after.voice.mention}", inline=False)
            elif after.voice is None:
                embed.add_field(name="Canal vocal", value=f"{before.mention} s'est déconnecté de {before.voice.mention}", inline=False)

        if before.roles != after.roles:
            added = [role.name for role in after.roles if role not in before.roles]
            removed = [role.name for role in before.roles if role not in after.roles]

            if added:
                embed.add_field(name="Rôle(s) ajouté(s)", value=", ".join(added))
            if removed:
                embed.add_field(name="Rôle(s) supprimé(s)", value=", ".join(removed))

        if embed.fields:
            await self.say(configs.LOGS_CHANNEL, embed=embed)
        

    async def on_guild_channel_create(self, channel: disnake.TextChannel):
        embed = disnake.Embed(title="Canal créé", color=0x00ff00)

        logs = await channel.guild.audit_logs(limit=1, action=disnake.AuditLogAction.channel_create).flatten()
        embed.add_field(name="Nom", value=f"{channel.mention}")
        if logs:
            embed.add_field(name="Créé par", value=logs[0].user.mention, inline=False)
        else:
            embed.add_field(name="Créé par", value="Inconnu", inline=False)

        if embed.fields:
            await self.say(configs.LOGS_CHANNEL, embed=embed)

    async def on_guild_channel_remove(self, channel: disnake.TextChannel):
        embed = disnake.Embed(title="Canal supprimé", color=0x00ff00)
        
        logs = await channel.guild.audit_logs(limit=1, action=disnake.AuditLogAction.channel_delete).flatten()
        embed.add_field(name="Nom", value=f"{channel.mention}")
        if logs:
            embed.add_field(name="Supprimé par", value=logs[0].user.mention, inline=False)
        else:
            embed.add_field(name="Supprimé par", value="Inconnu", inline=False)

        if embed.fields:
            await self.say(configs.LOGS_CHANNEL, embed=embed)

    async def on_guild_channel_update(self, before: disnake.abc.GuildChannel, after: disnake.abc.GuildChannel):
        embed = disnake.Embed(title="Canal modifié", color=0x00ff00)

        logs = await before.guild.audit_logs(limit=1, action=disnake.AuditLogAction.channel_update).flatten()
        if before.name != after.name:
            embed.add_field(name="Nom", value=f"{before.mention} -> {after.mention}")
        
        if before.category != after.category:
            if before.category is None:
                embed.add_field(name="Catégorie", value=f"{before.mention} a été déplacé dans {after.category.mention}")
            elif after.category is None:
                embed.add_field(name="Catégorie", value=f"{before.mention} a été déplacé de {before.category.mention}")
            elif after.category is not None and before.category is not None:
                embed.add_field(name="Catégorie", value=f"{before.mention} a été déplacé de {before.category.mention} vers {after.category.mention}")
        
        if logs:
            embed.add_field(name="Modifié par", value=logs[0].user.mention, inline=False)
        else:
            embed.add_field(name="Modifié par", value="Inconnu", inline=False)

        if embed.fields:
            await self.say(configs.LOGS_CHANNEL, embed=embed)

    async def on_error(self, event, *args):
        if isinstance(event, NoReplyException):
            await util.exception(event.channel, event.message)
            return # We don't want to print the traceback
        
        traceback.print_exc()

    async def say(self, channel: disnake.TextChannel | str, *args, **kwargs):
        if type(channel) is str:
            # channel_id/server_id
            channel_id, server_id = channel.split("/")
            channel = self.get_guild(int(server_id)).get_channel(int(channel_id))
        try:
            return await channel.send(*args, **kwargs)
        except disnake.Forbidden as send_error:
            util.logger.warning(send_error)


if __name__ == "__main__":
    util.logger.info("Starting the bot!")
    client = AdeptClient(prefix=configs.PREFIX)
    client.run(configs.TOKEN)
