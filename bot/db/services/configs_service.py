"""Service for dynamic bot configs."""

from bot.db.models import SpamConfigs
from bot.db.models.bot_configs import GlobalConfig
from bot.db.services import BaseService


class ConfigsService(BaseService):
    """Service for dynamic bot configs."""
    __COLLECTION_NAME = "configs"

    def find_or_create_spam_configs(self) -> SpamConfigs:
        """Find or create the spam configs."""
        data = self.find_one({"_id": "spam"})

        spam_config = SpamConfigs()
        if data is None:
            self.insert_one(spam_config.__dict__)

            return spam_config

        for attr in spam_config.__slots__:
            setattr(spam_config, attr, data[attr])

        return spam_config

    def update_configs(self, config: GlobalConfig):
        """
        Update the configs.

        Parameters
        ----------
        `config` : GlobalConfig
            The config to update.
        """
        return self.update_one({"_id": config.config_id}, config.__dict__, upsert=True)

    @property
    def collection_name(self):
        return self.__COLLECTION_NAME
