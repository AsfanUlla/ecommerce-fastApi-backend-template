from fastapi.encoders import jsonable_encoder
from fastapi import HTTPException, status
from datetime import datetime
from bson import ObjectId
from pymongo import UpdateOne
from pymongo.errors import BulkWriteError


class MongoInterface:

    @staticmethod
    async def insert_one(collection_name, post_obj):
        post_obj = jsonable_encoder(post_obj)
        post_obj['cd'] = datetime.utcnow()
        doc = await collection_name.insert_one(post_obj)
        # doc = await db[collection_name].find_one({"_id": doc.inserted_id})
        return str(doc.inserted_id)

    @staticmethod
    async def find_or_404(collection_name, query, exclude=None, error_message="Item Not Found"):
        doc = await collection_name.find_one(query, exclude)
        if not doc:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=error_message)
        return doc

    @staticmethod
    async def find_or_none(collection_name, query, exclude=None, sort=None):
        if sort:
            return await collection_name.find_one(query, exclude, sort=sort)
        return await collection_name.find_one(query, exclude)

    @staticmethod
    async def find_all(collection_name, query=None, exclude=None, sort=None, list=1000):
        document = []
        if query is None:
            query = {}
        if exclude is None:
            exclude = {}
        exclude.update(dict(
            cd=False
        ))
        if sort:
            doc = await collection_name.find(query, exclude, sort=sort).to_list(list)
        else:
            doc = await collection_name.find(query, exclude).to_list(list)
        for d in doc:
            for key, item in d.items():
                if type(item) == ObjectId:
                    d[key] = str(item)
            document.append(d)
        return document

    @staticmethod
    async def bulk_update(**kwargs):
        try:
            if kwargs.get("q_type") == "set":
                await kwargs.get("collection_name").bulk_write(
                    [
                        UpdateOne(
                            {
                                '_id': ObjectId(key)
                            },
                            {
                                '$set': values
                            },
                            upsert=True
                        ) for key, values in kwargs.get("data").items()
                    ]
                )
            if kwargs.get("q_type") == "push":
                await kwargs.get("collection_name").bulk_write(
                    [
                        UpdateOne(
                            {
                                '_id': ObjectId(key)
                            },
                            {
                                '$push': values
                            },
                            upsert=True
                        ) for key, values in kwargs.get("data").items()
                    ]
                )
        except BulkWriteError as bwe:
            raise HTTPException(status_code=bwe.code, detail=str(bwe.details))
        return True
