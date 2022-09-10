import datetime
import discord
from datetime import datetime as date
from discord.ext import tasks

from bot import util
from bot.strikes import Strike
from bot.task import Task

task_list = []


async def create_mute_task(member: discord.Member, duration: int = None):
    if duration is None:
        return await util.mute(member)

    end_date = date.now() + datetime.timedelta(seconds=duration)
    task = Task(member, end_date, Strike.MUTE)

    exists = any(task for task in task_list if task.member.id == member.id)
    if exists:
        task_list.remove(task for task in task_list if task.member.id == member.id)

    task_list.append(task)

    if not process_mutes.is_running():
        process_mutes.start()

    await util.mute(member)


async def delete_task(member: discord.Member, strike_type: Strike, reason: str = "Automatic moderation"):
    if strike_type == Strike.MUTE:
        # TODO: Api call
        await util.unmute(member, reason)
    elif strike_type == Strike.BAN:
        # TODO: Api call
        # TODO: Remove ban
        pass

    task = [task for task in task_list if task.member.id == member.id and task.type == strike_type]
    if len(task) > 0:
        task = task[0]
        task_list.remove(task)


@tasks.loop(seconds=1)
async def process_mutes():
    now = date.now()
    for task in task_list:
        if task.end_date <= now:
            await delete_task(task.member, task.type)

    if len(task_list) == 0:
        process_mutes.stop()


def _load_tasks():
    # TODO: Fetch from API
    to_process = []

    global task_list
    for task in to_process:
        # Just to make the code more readable
        member = util.get_member(task['guild'], task['member'])
        end_date = datetime.datetime.strptime(task['end_date'], "%Y-%m-%d %H:%M:%S.%f")

        task_list.append(Task(member, end_date, task['type']))

    if len(task_list) > 0:
        process_mutes.start()
