"""
MongoDB database
"""
from pymongo import MongoClient
import uuid


class MongoDBDatabase:
    """
    MongoDB database class
    """
    def __init__(self, uri, db_name, collection_name):
        self.client = MongoClient(uri)
        self.db = self.client[db_name]
        self.collection = self.db[collection_name]

    def save_item(self, item_data: dict, id: str = None):
        """
        Save the item in the MongoDB collection
        """
        if not id:
            id = str(uuid.uuid4())
        item_data['_id'] = id
        self.collection.replace_one({'_id': id}, item_data, upsert=True)
        return id

    def get_list(self, sort_attr: str = None, sort_order: str = "desc"):
        """
        Returns the items in the MongoDB collection
        """
        sort_order = -1 if sort_order == "desc" else 1
        if sort_attr:
            items = list(self.collection.find().sort(sort_attr, sort_order))
        else:
            items = list(self.collection.find())
        return items

    def get_item(self, id: str):
        """
        Returns the item from the MongoDB collection
        """
        return self.collection.find_one({'_id': id})

    def delete_item(self, id: str):
        """
        Delete an item from the MongoDB collection
        """
        self.collection.delete_one({'_id': id})


# Example usage:
# db = MongoDBDatabase(
#     uri="mongodb://localhost:27017",
#     db_name="my_db",
#     collection_name="my_collection"
# )
# db.save_item({"name": "Item 1", "value": 100})
# item = db.get_item("some_id")
# db.delete_item("some_id")
