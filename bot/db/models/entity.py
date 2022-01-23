from abc import abstractproperty
from datetime import datetime

from ..services import BaseService


class Entity:
    def __init__(self, _id: int, created_at: datetime = None, updated_at: datetime = None):
        self._id = _id
        self.created_at = created_at
        self.updated_at = updated_at

        if self._id is not None:
            self.load()

    def save(self, upsert=True):
        if self.created_at is None:
            self.created_at = datetime.utcnow()
            self.updated_at = self.created_at
        else:
            self.updated_at = datetime.utcnow()
        
        return self.service.update_one({"_id": self._id}, {"$set": self.__dict__}, upsert=upsert)

    def delete(self):
        return self.service.delete_one({"_id": self._id})

    def load(self):
        entity: dict = self.service.find_one({"_id": self._id})

        if entity is not None:
            self.created_at = entity.get("created_at")
            self.updated_at = entity.get("updated_at")

    @abstractproperty
    def service(self) -> BaseService:
        pass
