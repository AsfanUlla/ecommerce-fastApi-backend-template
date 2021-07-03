from fastapi import APIRouter, Body, HTTPException, status, Header
from fastapi.responses import JSONResponse
from fastapi.encoders import jsonable_encoder
from common.models import SchemalessResponse
from common.views import MongoInterface
from common.db import collections
from super.models import *
from common.utils import verify_token
from bson import ObjectId

router = APIRouter()


@router.get("/userlist", response_model=SchemalessResponse)
async def user_list(token: str = Header(...)):
    user, payload = await verify_token(token)
    if not user["is_su_admin"]:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Illegal token")
    users_list = await MongoInterface.find_all(
        collections['users'],
        exclude=dict(
            passwd=False
        )
    )
    response = SchemalessResponse(
        data=dict(
            users_list=users_list,
            success=True
        ),
        message="user list delivered"
    )

    return JSONResponse(jsonable_encoder(response))


@router.post("/user_permissions", response_model=SchemalessResponse)
async def user_permissions(data: Dict[str, UserUpdateData] = Body(...), token: str = Header(...)):
    user, payload = await verify_token(token)
    if not user["is_su_admin"]:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Illegal token")
    data = jsonable_encoder(data)
    update_users = await MongoInterface.bulk_update(
        collection_name=collections['users'],
        data=data,
        q_type='set'
    )

    response = SchemalessResponse(
        data=dict(
            success=update_users
        ),
        message="user list updated"
    )

    return JSONResponse(jsonable_encoder(response))
