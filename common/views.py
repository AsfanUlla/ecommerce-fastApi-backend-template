from fastapi.encoders import jsonable_encoder
from fastapi import HTTPException, status
from datetime import datetime
from bson import ObjectId
from pymongo import UpdateOne
from pymongo.errors import BulkWriteError


class PyObjectId(ObjectId):
    @classmethod
    def __get_validators__(cls):
        yield cls.validate

    @classmethod
    def validate(cls, v):
        if not ObjectId.is_valid(v):
            raise ValueError("Invalid objectid")
        return ObjectId(v)

    @classmethod
    def __modify_schema__(cls, field_schema):
        field_schema.update(type="string")


class MongoInterface:

    @staticmethod
    async def insert_one(collection_name, post_obj, exist_query=None, error_message="DOC exists"):
        if exist_query:
            doc_exist = await collection_name.find_one(exist_query, {"_id": 1})
            if doc_exist:
                raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=error_message)
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
            elif kwargs.get("q_type") == "push":
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
            else:
                raise HTTPException(status.HTTP_400_BAD_REQUEST, detail="Invalid query type")
        except BulkWriteError as bwe:
            raise HTTPException(status_code=bwe.code, detail=str(bwe.details))
        return True

    @staticmethod
    async def update_doc(**kwargs):
        if kwargs.get("q_type") == 'push':
            return await kwargs.get("collection_name").update_one(
                kwargs.get("query"),
                {"$push": kwargs.get("update_data")},
                upsert=True
            )
        elif kwargs.get("q_type") == 'set':
            return await kwargs.get("collection_name").update_one(
                kwargs.get("query"),
                {"$set": kwargs.get("update_data")},
                upsert=True
            )
        else:
            raise HTTPException(status.HTTP_400_BAD_REQUEST, detail="Invalid query type")
