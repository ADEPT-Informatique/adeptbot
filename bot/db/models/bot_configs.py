"""Models for dynamic bot configs."""

from bot.db.models.entity import Entity


class GlobalConfig(Entity):
    """
    Model for global configs.

    Attributes
    ----------
    `config_id` : str
        The name of the config.
    """

    __slots__ = ("_id",)

    def __init__(self, _id: str) -> None:
        """
        Parameters
        ----------
        `_id` : str
            The name of the config.
        """
        super().__init__(_id)

    @property
    def config_id(self):
        """The id of the config."""
        return self._id


class SpamConfigs(GlobalConfig):
    """
    Model for spam configs.

    Attributes
    ----------
    `repetition` : int
        The number of messages that can be sent before being muted.
    `mute_time` : int
        The time in seconds that a user will be muted for.
    """

    __slots__ = ("repetition", "mute_time")

    def __init__(self) -> None:
        super().__init__("spam")
        self.repetition = 3
        self.mute_time = 90
