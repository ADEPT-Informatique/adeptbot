from . import BaseService


class UserService(BaseService):
    __COLLECTION_NAME = "users"

    def __init__(self):
        super().__init__()

    @property
    def collection_name(self):
        return self.__COLLECTION_NAME
