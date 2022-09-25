from abc import abstractproperty
from pymongo import MongoClient
from pymongo.database import Database

import configs


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

    def insert_one(self, data, **kwargs):
        return self.conn().get_collection(self.collection_name).insert_one(data, **kwargs)

    def find_one(self, filter, **kwargs):
        return self.conn().get_collection(self.collection_name).find_one(filter, **kwargs)

    def find(self, filter, **kwargs):
        return self.conn().get_collection(self.collection_name).find(filter, **kwargs)

    def find_all(self):
        return self.conn().get_collection(self.collection_name).find()

    def update_one(self, filter, data, **kwargs):
        return self.conn().get_collection(self.collection_name).update_one(filter, data, **kwargs)

    def delete_one(self, filter, **kwargs):
        return self.conn().get_collection(self.collection_name).delete_one(filter, **kwargs)

    def delete_many(self, filter, **kwargs):
        return self.conn().get_collection(self.collection_name).delete_many(filter, **kwargs)
