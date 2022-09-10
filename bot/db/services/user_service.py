from . import BaseService


class UserService(BaseService):
    __COLLECTION_NAME = "users"

    def __init__(self):
        super().__init__()

    def find_by_id(self, id: int):
        return self.find_one({"_id": id})

    @property
    def collection_name(self):
        return self.__COLLECTION_NAME
