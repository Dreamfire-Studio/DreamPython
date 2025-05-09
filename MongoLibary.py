import pymongo

class MongoLibary:
    def __init__(self, url, db_name):
        self.client = pymongo.MongoClient(url)
        self.database = self.client[db_name]

    def get_collection(self, collection_name):
        return self.database[collection_name]

    def insert_document(self, collection_name, document):
        collection = self.get_collection(collection_name)
        return collection.insert_one(document)

    def find(self, collection_name, query):
        collection = self.get_collection(collection_name)
        return collection.find(query)

    def find_one(self, collection_name, query):
        collection = self.get_collection(collection_name)
        return collection.find_one(query)

    def find_documents(self, collection_name, query=None):
        collection = self.get_collection(collection_name)
        return collection.find(query) if query else collection.find()

    def update_documents(self, collection_name, query, update):
        collection = self.get_collection(collection_name)
        return collection.update_one(query, {'$set': update})

    def delete_document(self, collection_name, query):
        collection = self.get_collection(collection_name)
        return collection.delete_one(query)

    def count_documents(self, collection_name, query=None):
        collection = self.get_collection(collection_name)
        return collection.count_documents(query) if query else collection.count_documents({})

    def close_connection(self):
        self.client.close()