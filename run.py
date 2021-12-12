import asyncio
import discord
import traceback
from discord.ext import commands

import configs
from bot import tasks, users, util, welcome
from bot.botcommands import member, moderation
from bot.interactions import TicketOpeningInteraction, TicketCloseInteraction
from bot.welcome import NoReplyException


class AdeptClient(commands.Bot):
    def __init__(self, prefix):
        intents = discord.Intents.default()
        intents.members = True
        loop = asyncio.get_event_loop_policy().new_event_loop()
        super().__init__(prefix, loop=loop, intents=intents)

        self.add_cog(member.MemberCog())
        self.add_cog(moderation.ModerationCog(self))
        self.persistent_views_loaded = False

    async def on_ready(self):
        util._load(self)
        util.logger.info(f"\nLogged in with account @{self.user.name} ID:{self.user.id} \n------------------------------------\n")
        
        if not self.persistent_views_loaded:
            self.add_view(TicketOpeningInteraction())
            self.add_view(TicketCloseInteraction())
            self.persistent_views_loaded = True

        await self.change_presence(activity=discord.Activity(name="for bad boys!", type=discord.ActivityType.watching))
        tasks._load_tasks(self)

    async def on_message(self, message: discord.Message):
        if (message.author.bot):
            return

        member = message.author
        user: users.User = await users.get_user(member)
        if user is None:
            user = await users.create_user(member)

        if (message.created_at.timestamp() - user.last_message_timestamp) < 0.5:
            user.strikes += 1
            
            if user.strikes % 3:
                if member.get_role(configs.ADMIN_ROLE) is None and member.get_role(configs.TRUST_ROLE) is None:
                    times = user.strikes / 3
                    await tasks.create_mute_task(member, 60 * times)
                    await message.channel.send(f"{member.mention} est maintenant muet en raison du spam!")
                user.strikes = 0
        else:
            user.strikes = 0

        user.last_message_timestamp = message.created_at.timestamp()

        message.content = message.content.replace(f"<@!{self.user.id}>", configs.PREFIX, 1) if message.content.startswith(f"<@!{self.user.id}>") else message.content
        message.content = message.content.replace(f"<@{self.user.id}>", configs.PREFIX, 1) if message.content.startswith(f"<@{self.user.id}>") else message.content

        if message.content.startswith(configs.PREFIX):
            await self.process_commands(message)

    async def on_message_edit(self, before: discord.Message, after: discord.Message):
        if before.author.bot:
            return

        embed = discord.Embed(title="Message édité", color=0x00ff00, timestamp=discord.utils.utcnow(), url=after.jump_url)

        if before.content != after.content:
            embed.add_field(name="Contenu avant", value=before.content)
            embed.add_field(name="Contenu après", value=after.content, inline=False)

        if embed.fields:
            await self.say(configs.LOGS_CHANNEL, embed=embed)

    async def on_message_delete(self, message: discord.Message):
        embed = discord.Embed(title="Message supprimé", color=0xff0000, timestamp=discord.utils.utcnow())
        embed.add_field(name="Contenu", value=message.content, inline=False)

        if message.author.id != self.user.id:
            logs = await message.guild.audit_logs(limit=1, action=discord.AuditLogAction.message_delete).flatten()
            if logs:
                embed.add_field(name="Supprimé par", value=logs[0].user.mention, inline=False)
            else:
                embed.add_field(name="Supprimé par", value="Inconnu", inline=False)

        await self.say(configs.LOGS_CHANNEL, embed=embed)

    async def on_member_join(self, member: discord.Member):
        await self.say(configs.LOGS_CHANNEL, f"{member.mention} a rejoint le serveur.")
        await self.say(configs.WELCOME_CHANNEL, configs.WELCOME_SERVER.format(name=member.mention))
        result = await welcome.walk_through_welcome(member)

        await welcome.process_welcome_result(member, result)

    async def on_member_remove(self, member: discord.Member):
        await self.say(configs.LOGS_CHANNEL, f"{member.mention} a quitté le serveur.")

    async def on_member_update(self, before: discord.Member, after: discord.Member):
        embed = discord.Embed(title="Membre modifié", color=0x00ff00)
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
        

    async def on_guild_channel_create(self, channel: discord.TextChannel):
        embed = discord.Embed(title="Canal créé", color=0x00ff00)

        logs = await channel.guild.audit_logs(limit=1, action=discord.AuditLogAction.channel_create).flatten()
        embed.add_field(name="Nom", value=f"{channel.mention}")
        if logs:
            embed.add_field(name="Créé par", value=logs[0].user.mention, inline=False)
        else:
            embed.add_field(name="Créé par", value="Inconnu", inline=False)

        if embed.fields:
            await self.say(configs.LOGS_CHANNEL, embed=embed)

    async def on_guild_channel_remove(self, channel: discord.TextChannel):
        embed = discord.Embed(title="Canal supprimé", color=0x00ff00)
        
        logs = await channel.guild.audit_logs(limit=1, action=discord.AuditLogAction.channel_delete).flatten()
        embed.add_field(name="Nom", value=f"{channel.mention}")
        if logs:
            embed.add_field(name="Supprimé par", value=logs[0].user.mention, inline=False)
        else:
            embed.add_field(name="Supprimé par", value="Inconnu", inline=False)

        if embed.fields:
            await self.say(configs.LOGS_CHANNEL, embed=embed)

    async def on_guild_channel_update(self, before: discord.abc.GuildChannel, after: discord.abc.GuildChannel):
        embed = discord.Embed(title="Canal modifié", color=0x00ff00)

        logs = await before.guild.audit_logs(limit=1, action=discord.AuditLogAction.channel_update).flatten()
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

    async def say(self, channel: discord.TextChannel | str, *args, **kwargs):
        if type(channel) is str:
            # channel_id/server_id
            channel_id, server_id = channel.split("/")
            channel = self.get_guild(int(server_id)).get_channel(int(channel_id))
        try:
            return await channel.send(*args, **kwargs)
        except discord.Forbidden as send_error:
            util.logger.warning(send_error)


if __name__ == "__main__":
    util.logger.info("Starting the bot!")
    client = AdeptClient(prefix=configs.PREFIX)
    client.run(configs.TOKEN)
