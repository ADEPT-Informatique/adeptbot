"""Base service class for all services."""

from abc import abstractmethod

from pymongo import MongoClient
from pymongo.cursor import Cursor
from pymongo.database import Database
from pymongo.results import DeleteResult, InsertOneResult, UpdateResult

import configs


class BaseService:
    """
    Base service class for all services.

    Methods
    -------
    `conn` : Database
        Return a connection to the database.
    `find` : Cursor
        Find documents in the database.
    `find_one` : Cursor
        Find a single document in the database.
    `insert_one` : InsertOneResult
        Insert a document into the database.
    `update_one` : UpdateResult
        Update a document in the database.
    `delete_one` : DeleteResult
        Delete a document from the database.

    Attributes
    ----------
    `collection_name` : str
        The name of the collection.
    """

    def __init__(self):
        self.__conn = None

    def conn(self) -> Database:
        """Return a connection to the database."""
        if self.__conn is None:
            self.__conn = MongoClient(
                "mongodb+srv://" +
                f"{configs.DB_USER}:{configs.DB_PASSWORD}" +
                f"@{configs.DB_HOST}/" +
                "?retryWrites=true&w=majority&ssl=true",
            ).get_database(configs.DB_NAME)

        return self.__conn

    @property
    @abstractmethod
    def collection_name(self):
        """Return the collection name."""

    def _get_collection(self):
        return self.conn().get_collection(self.collection_name)

    def find(self, filters: dict, **kwargs) -> Cursor:
        """
        Find documents in the database.

        Parameters
        ----------
        `filters` : dict
            The filters to use.
        `kwargs` : dict
            The arguments to pass to the find
        """
        return self._get_collection().find(filters, **kwargs)

    def find_one(self, filters: dict, **kwargs) -> Cursor:
        """
        Find a single document in the database.

        Parameters
        ----------
        `filters` : dict
            The filters to use.
        `kwargs` : dict
            The arguments to pass to the find_one
        """
        return self._get_collection().find_one(filters, **kwargs)

    def find_all(self, **kwargs) -> Cursor:
        """
        Find all documents in the database.

        Parameters
        ----------
        `kwargs` : dict
            The arguments to pass to the find
        """
        return self.find(**kwargs)

    def insert_one(self, data: dict, **kwargs) -> InsertOneResult:
        """
        Insert a single document into the database.

        Parameters
        ----------
        `data` : dict
            The data to insert.
        `kwargs` : dict
            The arguments to pass to the insert_one
        """
        return self._get_collection().insert_one(data, **kwargs)

    def update_one(self, filters: dict, data: dict, **kwargs) -> UpdateResult:
        """
        Update a single document in the database.

        Parameters
        ----------
        `filters` : dict
            The filters to use.
        `data` : dict
            The data to update.
        `kwargs` : dict
            The arguments to pass to the update_one
        """
        return self._get_collection().update_one(filters, {"$set": data}, **kwargs)

    def delete_one(self, filters: dict, **kwargs) -> DeleteResult:
        """
        Delete a document in the database.

        Parameters
        ----------
        `filters` : dict
            The filters to use.
        `kwargs` : dict
            The arguments to pass to the delete_one
        """
        return self._get_collection().delete_one(filters, **kwargs)
