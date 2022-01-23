import disnake
from disnake.ext import commands

import configs


class LoggingCog(commands.Cog):
    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot

    @commands.Cog.listener()
    async def on_message_edit(self, before: disnake.Message, after: disnake.Message):
        if before.author.bot:
            return

        author = after.author
        embed = disnake.Embed(description=f"**Message modifié dans {after.channel.mention}** [Allez au message]({after.jump_url})", 
                            color=0xF9E18B, 
                            timestamp=disnake.utils.utcnow())
        embed.set_author(name=f"{author}", icon_url=author.avatar.url)
        embed.set_footer(text=f"ID: {author.id}")

        if before.content != after.content:
            embed.add_field(name="Contenu avant", value=before.content)
            embed.add_field(name="Contenu après", value=after.content, inline=False)

            await self.bot.say(configs.LOGS_CHANNEL, embed=embed)

    @commands.Cog.listener()
    async def on_message_delete(self, message: disnake.Message):
        if message.author.bot:
            return

        author = message.author
        embed = disnake.Embed(color=0xff0000, timestamp=disnake.utils.utcnow())
        embed.set_author(name=f"{author}", icon_url=author.avatar.url)
        embed.set_footer(text=f"ID: {author.id}")
        
        logs = await message.guild.audit_logs(limit=1, action=disnake.AuditLogAction.message_delete).flatten()
        if logs:
            embed.description = f"Message envoyé par {author.mention} a été supprimé par {logs[0].user.mention} dans {message.channel.mention}"
        else:
            embed.description = f"Message envoyé par {author.mention} a été supprimé dans {message.channel.mention}"

            await self.bot.say(configs.LOGS_CHANNEL, embed=embed)

    @commands.Cog.listener()
    async def on_member_join(self, member: disnake.Member):
        await self.bot.say(configs.LOGS_CHANNEL, f"{member.mention} a rejoint le serveur.")

    @commands.Cog.listener()
    async def on_member_remove(self, member: disnake.Member):
        await self.bot.say(configs.LOGS_CHANNEL, f"{member.mention} a quitté le serveur.")

    @commands.Cog.listener()
    async def on_member_update(self, before: disnake.Member, after: disnake.Member):
        embed = disnake.Embed(color=0xF9E18B, timestamp=disnake.utils.utcnow())
        embed.set_author(name=f"{after}", icon_url=after.avatar.url)
        embed.set_footer(text=f"ID: {after.id}")

        if before.nick != after.nick:
            embed.description = f"**{after.mention} a changé de pseudo de ``{before.nick}`` à ``{after.nick}``**"

            await self.bot.say(configs.LOGS_CHANNEL, embed=embed)

        if before.roles != after.roles:
            added = [role.name for role in after.roles if role not in before.roles]
            removed = [role.name for role in before.roles if role not in after.roles]

            if len(added) > 0:
                embed.description = f"**Le rôle ``{added[0]}`` a été ajouté à {after.mention}**"
            if len(removed) > 0:
                embed.description = f"**Le rôle ``{removed[0]}`` a été retiré à {after.mention}**"

            await self.bot.say(configs.LOGS_CHANNEL, embed=embed)

    @commands.Cog.listener()
    async def on_voice_state_update(self, member: disnake.Member, before: disnake.VoiceState, after: disnake.VoiceState):
        embed = disnake.Embed(color=0xF9E18B, timestamp=disnake.utils.utcnow())
        embed.set_author(name=f"{member}", icon_url=member.avatar.url)
        embed.set_footer(text=f"ID: {member.id}")

        if before.channel != after.channel:
            if before.channel is None:
                embed.description = f"**{member.mention} a rejoint le salon vocal {after.channel.mention}**"
            elif after.channel is None:
                embed.description = f"**{member.mention} s'est déconnecté de {before.channel.mention}**"
            else:
                embed.description = f"**{member.mention} a changé de salon vocal: ``#{before.channel.name}`` -> ``#{after.channel.name}``**"

            await self.bot.say(configs.LOGS_CHANNEL, embed=embed)
        
    @commands.Cog.listener()
    async def on_guild_channel_create(self, channel: disnake.abc.GuildChannel):
        embed = disnake.Embed(color=0x99CC99, timestamp=disnake.utils.utcnow())
        embed.set_author(name=f"{channel.guild}", icon_url=channel.guild.icon.url)

        logs = await channel.guild.audit_logs(limit=1, action=disnake.AuditLogAction.channel_create).flatten()
        if logs:
            author = logs[0].user
            embed.description = f"**{channel.mention} a été créé par {author.mention}**"
        else:
            embed.description = f"**{channel.mention} a été créé**"

        await self.bot.say(configs.LOGS_CHANNEL, embed=embed)

    @commands.Cog.listener()
    async def on_guild_channel_remove(self, channel: disnake.abc.GuildChannel):
        embed = disnake.Embed(color=0xF9E18B, timestamp=disnake.utils.utcnow())
        embed.set_author(name=f"{channel.guild}", icon_url=channel.guild.icon.url)

        logs = await channel.guild.audit_logs(limit=1, action=disnake.AuditLogAction.channel_create).flatten()
        if logs:
            author = logs[0].user
            embed.set_footer(text=f"ID: {author.id}")
            embed.description = f"**{channel.mention} a été supprimé par {author.mention}**"
        else:
            embed.description = f"**{channel.mention} a été supprimé**"

        await self.bot.say(configs.LOGS_CHANNEL, embed=embed)

    @commands.Cog.listener()
    async def on_guild_channel_update(self, before: disnake.abc.GuildChannel, after: disnake.abc.GuildChannel):
        embed = disnake.Embed(color=0xF9E18B, timestamp=disnake.utils.utcnow())
        embed.set_author(name=f"{after.guild}", icon_url=after.guild.icon.url)

        logs = await before.guild.audit_logs(limit=1, action=disnake.AuditLogAction.channel_update).flatten()
        if before.name != after.name:
            if logs:
                author = logs[0].user
                embed.set_footer(text=f"ID: {author.id}")
                embed.description = f"**{before} a été renommé pour {after.mention} par {author.mention}**"
            else:
                embed.description = f"**{before} a été renommé pour {after.mention}**"

            await self.bot.say(configs.LOGS_CHANNEL, embed=embed)
