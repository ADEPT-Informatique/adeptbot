"""This module contains the permission system for the bot."""

from enum import Enum
from functools import total_ordering

import discord

import configs


class InsufficientPermissionsError(PermissionError):
    """
    This exception is raised when a member doesn't have the required permissions to perform an action.

    Parameters:
    -----------
    `channel` : discord.abc.Messageable
        The channel the error message will be sent in.
    `message` : str
        The message that will be sent to the user.
    """

    def __init__(self, channel: discord.abc.Messageable,
                 message: str = "Vous n'avez pas les permissions nécessaire pour effectuer cette action!") -> None:
        self.channel = channel
        self.message = message


@total_ordering
class Permission(Enum):
    """This class represents the permission level of a member."""

    def __gt__(self, other):
        return self.value > other.value

    def __lt__(self, other):
        return self.value < other.value

    def __eq__(self, other):
        return self.value == other.value

    REGULAR = 0  # Regular Member
    TRUSTED = 1  # MDC
    ADMIN = 2  # Admin


def determine_permission(member: discord.Member) -> Permission:
    """
    This function determines the permission level of a member.

    Parameters:
    -----------
    `member` : discord.Member
        The member to determine the permission level of.
    """
    is_admin = member.get_role(configs.ADMIN_ROLE)
    is_trust = member.get_role(configs.TRUST_ROLE)

    if is_admin:
        return Permission.ADMIN
    elif is_trust:
        return Permission.TRUSTED
    else:
        return Permission.REGULAR


def has_permission(member: discord.Member, permission: Permission):
    """
    This function checks if a member has the required permission level.

    Parameters:
    ----------
    `member` : discord.Member
        The member to check the permission level of.
    `permission` : Permission
        The required permission level.
    """
    member_perm = determine_permission(member)

    return member_perm >= permission
