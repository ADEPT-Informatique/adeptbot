"""Models for dynamic bot configs."""


class GlobalConfig:
    """Model for global configs."""
    _id: str

    def __init__(self, _id) -> None:
        self._id = _id


class SpamConfigs(GlobalConfig):
    """Model for spam configs."""
    __slots__ = ["repetition", "mute_time"]

    repetition: int
    mute_time: int

    def __init__(self) -> None:
        super().__init__("spam")
        self.repetition = 3
        self.mute_time = 90
