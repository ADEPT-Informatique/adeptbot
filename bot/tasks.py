"""
This module contains the task class and the task list.
It also contains the task loop that checks if a task is finished.
"""

import datetime
from datetime import datetime as date
from typing import List

import discord
from discord.ext import tasks

from bot import util
from bot.strikes import Strike
from bot.task import Task

TASK_LIST: List[Task] = []


async def create_mute_task(member: discord.Member, duration: int = None, reason: str = None):
    """
    Creates a mute task for the given member.

    Parameters
    ----------
    `member` : discord.Member
        The member to mute.
    `duration` : int
        The duration in seconds.
    `reason` : str
        The reason of the mute.
    """
    if duration is None:
        return await util.mute(member, reason)

    end_date = date.now() + datetime.timedelta(seconds=duration)
    new_task = Task(member, end_date, Strike.MUTE)

    current_tasks = [task for task in TASK_LIST if task.member.id == member.id and task.type == new_task.type]
    if len(current_tasks) != 0:
        for current_task in current_tasks:
            TASK_LIST.remove(current_task)

    TASK_LIST.append(new_task)

    if not process_mutes.is_running():
        process_mutes.start()

    await util.mute(member, reason)


async def delete_task(member: discord.Member, strike_type: Strike, reason: str = "Automatic moderation"):
    """
    Deletes a task from the task list.

    Parameters
    ----------
    `member` : discord.Member
        The member to delete the task for.
    `strike_type` : Strike
        The type of the task to remove.
    `reason` : str
        The reason of the removal.
    """
    if strike_type == Strike.MUTE:
        # TODO: DB call
        await util.unmute(member, reason)
    elif strike_type == Strike.BAN:
        # TODO: DB call
        # TODO: Remove ban
        pass

    task = [task for task in TASK_LIST if task.member.id == member.id and task.type == strike_type]
    if len(task) > 0:
        task = task[0]
        TASK_LIST.remove(task)


@tasks.loop(seconds=1)
async def process_mutes():
    """
    This loop checks if a task is finished.
    If it is, it deletes the task and executes the action.
    """
    now = date.now()
    for task in TASK_LIST:
        if task.end_date <= now:
            await delete_task(task.member, task.type)

    if len(TASK_LIST) == 0:
        process_mutes.stop()


async def load_tasks(bot: discord.Client):
    """
    Loads all tasks from the database.

    NOTE: This function should **ONLY** be called once at startup.
    """
    # TODO: Fetch from DB
    to_process = []

    for task in to_process:
        # Just to make the code more readable
        member = bot.get_guild(task["guild"]).get_member(task["member"])
        end_date = datetime.datetime.strptime(task["end_date"], "%Y-%m-%d %H:%M:%S.%f")

        TASK_LIST.append(Task(member, end_date, task["type"]))

    if len(TASK_LIST) > 0:
        process_mutes.start()
