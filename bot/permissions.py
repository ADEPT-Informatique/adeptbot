import disnake
from enum import Enum
from functools import total_ordering

import configs


class InsufficientPermissionsError(PermissionError):
    def __init__(self, channel: disnake.abc.Messageable, message: str = "Vous n'avez pas les permissions nécessaire pour effectuer cette action!") -> None:
        self.channel = channel
        self.message = message


@total_ordering
class Permission(Enum):
    def __gt__(self, other):
        return self.value > other.value

    def __lt__(self, other):
        return self.value < other.value

    def __eq__(self, other):
        return self.value == other.value

    REGULAR = 0 # Regular Member
    TRUSTED = 1 # MDC
    ADMIN = 2 # Admin


def determine_permission(member: disnake.Member) -> Permission:
    is_admin = member.get_role(configs.ADMIN_ROLE)
    is_trust = member.get_role(configs.TRUST_ROLE)

    if is_admin:
        return Permission.ADMIN
    elif is_trust:
        return Permission.TRUSTED
    else:
        return Permission.REGULAR


def has_permission(member: disnake.Member, permission: Permission):
    member_perm = determine_permission(member)

    return member_perm >= permission
