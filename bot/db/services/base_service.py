"""Base service class for all services."""

from abc import abstractmethod

from pymongo import MongoClient
from pymongo.cursor import Cursor
from pymongo.database import Database
from pymongo.results import DeleteResult, InsertOneResult, UpdateResult

import configs


class BaseService:
    """Base service class for all services."""

    def __init__(self):
        self.__conn = None

    def conn(self) -> Database:
        """Return a connection to the database."""
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

    @property
    @abstractmethod
    def collection_name(self):
        """Return the collection name."""

    def find(self, filters: dict, **kwargs) -> Cursor:
        """
        Find documents in the database.

        Parameters
        ----------
        - `filters` The filters to use.
        - `kwargs` The kwargs to pass to the find

        Returns
        -------
        The result of the query.
        """
        return self.conn().get_collection(self.collection_name).find(filters, **kwargs)

    def find_one(self, filters: dict, **kwargs) -> Cursor:
        """
        Find a single document in the database.

        Parameters
        ----------
        - `filters` The filters to use.
        - `kwargs` The kwargs to pass to the find_one

        Returns
        -------
        The result of the query.
        """
        return self.conn().get_collection(self.collection_name).find_one(filters, **kwargs)

    def find_all(self, **kwargs) -> Cursor:
        """Find all documents in the database."""
        return self.conn().get_collection(self.collection_name).find(**kwargs)

    def insert_one(self, data: dict, **kwargs) -> InsertOneResult:
        """
        Insert a single document into the database.

        Parameters
        ----------
        - `data` The data to insert.
        - `kwargs` The kwargs to pass to the insert_one

        Returns
        -------
        The result of the insert.
        """
        return self.conn().get_collection(self.collection_name).insert_one(data, **kwargs)

    def update_one(self, filters: dict, data: dict, **kwargs) -> UpdateResult:
        """
        Update a single document in the database.

        Parameters
        ----------
        - `filters` The filters to use.
        - `data` The data to update.

        Returns
        -------
        The result of the update.
        """
        return self.conn().get_collection(self.collection_name).update_one(filters, {"$set": data}, **kwargs)

    def delete_one(self, filters: dict, **kwargs) -> DeleteResult:
        """
        Delete a document in the database.

        Parameters
        ----------
        - `filters` The filters to use.
        - `kwargs` The kwargs to pass to the delete_one

        Returns
        -------
        The result of the delete.
        """
        return self.conn().get_collection(self.collection_name).delete_one(filters, **kwargs)
