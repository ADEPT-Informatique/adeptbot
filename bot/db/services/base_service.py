from abc import abstractproperty

import configs
from pymongo import MongoClient
from pymongo.cursor import Cursor
from pymongo.database import Database
from pymongo.results import DeleteResult, InsertOneResult, UpdateResult


class BaseService:
    def __init__(self):
        self.__conn = None

    def conn(self) -> Database:
        if self.__conn is None:
            self.__conn = MongoClient(
                host=configs.DB_HOST,
                username=configs.DB_USER,
                password=configs.DB_PASSWORD,
                authMechanism="SCRAM-SHA-256"
            ).get_database(configs.DB_NAME)

            return self.__conn
        else:
            return self.__conn

    @abstractproperty
    def collection_name(self):
        pass

    def find(self, filter: dict, **kwargs) -> Cursor:
        return self.conn().get_collection(self.collection_name).find(filter, **kwargs)

    def find_one(self, filter: dict, **kwargs) -> Cursor:
        return self.conn().get_collection(self.collection_name).find_one(filter, **kwargs)

    def find_all(self) -> Cursor:
        return self.conn().get_collection(self.collection_name).find()

    def insert_one(self, data: dict, **kwargs) -> InsertOneResult:
        return self.conn().get_collection(self.collection_name).insert_one(data, **kwargs)

    def update_one(self, filter: dict, data: dict, **kwargs) -> UpdateResult:
        return self.conn().get_collection(self.collection_name).update_one(filter, {"$set": data}, **kwargs)

    def delete_one(self, filter: dict, **kwargs) -> DeleteResult:
        return self.conn().get_collection(self.collection_name).delete_one(filter, **kwargs)
