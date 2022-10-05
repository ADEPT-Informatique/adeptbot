import discord
from discord.ext import commands

import configs
from bot import util


class LoggingCog(commands.Cog):
    @commands.Cog.listener()
    async def on_message_edit(self, before: discord.Message, after: discord.Message):
        if before.author.bot:
            return

        author = after.author
        embed = discord.Embed(description=f"**Message modifié dans {after.channel.mention}** [Allez au message]({after.jump_url})", 
                            color=0xF9E18B, 
                            timestamp=discord.utils.utcnow())
        embed.set_author(name=f"{author}", icon_url=author.avatar.url)
        embed.set_footer(text=f"ID: {author.id}")

        if before.content != after.content:
            embed.add_field(name="Contenu avant", value=before.content)
            embed.add_field(name="Contenu après", value=after.content, inline=False)

            await util.say(configs.LOGS_CHANNEL, embed=embed)

    @commands.Cog.listener()
    async def on_message_delete(self, message: discord.Message):
        if message.author.bot:
            return

        author = message.author
        embed = discord.Embed(color=0xFC5233, timestamp=discord.utils.utcnow())
        embed.add_field(name="Contenu", value=message.content[0:4000])
        embed.set_author(name=f"{author}", icon_url=author.avatar.url)
        embed.set_footer(text=f"ID: {author.id}")

        embed.description = f"Message envoyé par {author.mention} a été supprimé dans {message.channel.mention}"

        await util.say(configs.LOGS_CHANNEL, embed=embed)

    @commands.Cog.listener()
    async def on_member_join(self, member: discord.Member):
        await util.say(configs.LOGS_CHANNEL, f"{member.mention} a rejoint le serveur.")

    @commands.Cog.listener()
    async def on_member_remove(self, member: discord.Member):
        await util.say(configs.LOGS_CHANNEL, f"{member.mention} a quitté le serveur.")

    @commands.Cog.listener()
    async def on_member_update(self, before: discord.Member, after: discord.Member):
        embed = discord.Embed(color=0xF9E18B, timestamp=discord.utils.utcnow())
        embed.set_author(name=f"{after}", icon_url=after.avatar.url)
        embed.set_footer(text=f"ID: {after.id}")

        if before.nick != after.nick:
            embed.description = f"**{after.mention} a changé de pseudo de ``{before.nick}`` à ``{after.nick}``**"

            await util.say(configs.LOGS_CHANNEL, embed=embed)

        if before.roles != after.roles:
            added = [role.name for role in after.roles if role not in before.roles]
            removed = [role.name for role in before.roles if role not in after.roles]

            if len(added) > 0:
                embed.description = f"**Le rôle ``{added[0]}`` a été ajouté à {after.mention}**"
            if len(removed) > 0:
                embed.description = f"**Le rôle ``{removed[0]}`` a été retiré à {after.mention}**"

            await util.say(configs.LOGS_CHANNEL, embed=embed)

    @commands.Cog.listener()
    async def on_voice_state_update(self, member: discord.Member, before: discord.VoiceState, after: discord.VoiceState):
        embed = discord.Embed(color=0xF9E18B, timestamp=discord.utils.utcnow())
        embed.set_author(name=f"{member}", icon_url=member.avatar.url)
        embed.set_footer(text=f"ID: {member.id}")

        if before.channel != after.channel:
            if before.channel is None:
                embed.description = f"**{member.mention} a rejoint le salon vocal {after.channel.mention}**"
            elif after.channel is None:
                embed.description = f"**{member.mention} s'est déconnecté de {before.channel.mention}**"
            else:
                embed.description = f"**{member.mention} a changé de salon vocal: ``#{before.channel.name}`` -> ``#{after.channel.name}``**"

            await util.say(configs.LOGS_CHANNEL, embed=embed)
        
    @commands.Cog.listener()
    async def on_guild_channel_create(self, channel: discord.abc.GuildChannel):
        embed = discord.Embed(color=0xF9E18B, timestamp=discord.utils.utcnow())
        embed.set_author(name=f"{channel.guild}", icon_url=channel.guild.icon.url)
        embed.set_footer(text=f"ID: {channel.guild.id}")

        embed.description = f"**#{channel.name} a été créé**"

        await util.say(configs.LOGS_CHANNEL, embed=embed)

    @commands.Cog.listener()
    async def on_guild_channel_delete(self, channel: discord.abc.GuildChannel):
        embed = discord.Embed(color=0xFC5233, timestamp=discord.utils.utcnow())
        embed.set_author(name=f"{channel.guild}", icon_url=channel.guild.icon.url)
        embed.set_footer(text=f"ID: {channel.guild.id}")

        embed.description = f"**#{channel.name} a été supprimé**"

        await util.say(configs.LOGS_CHANNEL, embed=embed)

    @commands.Cog.listener()
    async def on_guild_channel_update(self, before: discord.abc.GuildChannel, after: discord.abc.GuildChannel):
        embed = discord.Embed(color=0xF9E18B, timestamp=discord.utils.utcnow())
        embed.set_author(name=f"{after.guild}", icon_url=after.guild.icon.url)
        embed.set_footer(text=f"ID: {after.guild.id}")

        if before.name != after.name:
            embed.description = f"**``#{before}`` a été renommé pour {after.mention}**"
 
            await util.say(configs.LOGS_CHANNEL, embed=embed)
