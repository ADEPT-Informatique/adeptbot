import discord
from discord.ext import commands

import configs
from bot import tasks, users


class StrikesCog(commands.Cog):
    @commands.Cog.listener()
    async def on_message(self, message: discord.Message):
        if (message.author.bot or isinstance(message.channel, discord.DMChannel)):
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
