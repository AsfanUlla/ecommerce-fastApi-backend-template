from fastapi.encoders import jsonable_encoder
from fastapi import HTTPException, status
from common.db import db


class MongoInterface:

    @staticmethod
    async def insert_one(collection_name, post_obj):
        post_obj = jsonable_encoder(post_obj)
        doc = await db[collection_name].insert_one(post_obj)
        # doc = await db[collection_name].find_one({"_id": doc.inserted_id})
        return str(doc.inserted_id)

    @staticmethod
    async def find_or_404(collection_name, query, exclude=None, error_message="Item Not Found"):
        doc = await db[collection_name].find_one(query, exclude)
        if not doc:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=error_message)
        return doc

    @staticmethod
    async def find_or_none(collection_name, query, exclude=None, sort=None):
        if sort:
            return await db[collection_name].find_one(query, exclude, sort=sort)
        return await db[collection_name].find_one(query, exclude)
