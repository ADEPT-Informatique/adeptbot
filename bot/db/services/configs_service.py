from bot.db.models import SpamConfigs
from bot.db.models.bot_configs import GlobalConfig

from . import BaseService


class ConfigsService(BaseService):
    __COLLECTION_NAME = "configs"

    def __init__(self):
        super().__init__()

    def find_or_create_spam_configs(self) -> SpamConfigs:
        data = self.find_one({"_id": "spam"})

        spam_config = SpamConfigs()
        if data is None:
            self.insert_one(spam_config.__dict__)

            return spam_config

        for attr in spam_config.__dict__.keys():
            setattr(spam_config, attr, data[attr])
        
        return spam_config

    def update_configs(self, configs: GlobalConfig):
        return self.update_one({"_id": configs._id}, configs.__dict__, upsert=True)

    @property
    def collection_name(self):
        return self.__COLLECTION_NAME
