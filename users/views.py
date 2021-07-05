from fastapi import APIRouter, Body, HTTPException, status
from fastapi.responses import JSONResponse
from users.models import AddUserSchema, UserLoginSchema
from common.models import SchemalessResponse, EmailSchema
from fastapi.encoders import jsonable_encoder
from common.views import MongoInterface
from common.utils import get_password_hash, verify_password, create_access_token, send_mail, verify_token
from datetime import timedelta, datetime
from common.db import collections
from config import Config
from urllib import parse
from bson import ObjectId

router = APIRouter()


@router.post("/register", response_model=SchemalessResponse)
async def add_user(user: AddUserSchema = Body(..., )):
    user_doc = await MongoInterface.find_or_none(
        collections['users'],
        query=dict(
            email=user.email
        ), exclude=dict(
            _id=1
        )
    )
    if user_doc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="User already exist")
    user.passwd = get_password_hash(user.passwd)
    post_obj = jsonable_encoder(user)
    post_obj.update(
        dict(
            disabled=True,
            is_verified=False,
            is_teacher=False,
            is_admin=False,
            is_su_admin=False,
        )
    )
    user_add = await MongoInterface.insert_one(collections['users'], post_obj)
    verify_email_link = Config.HOST_URL + '/users/user_verification?verify_user=' + await create_access_token(
        data=dict(
            user_id=user_add
        ),
        key=Config.JWT_EMAIL_SECRET,
        expires_delta=timedelta(minutes=15)
    )
    await send_mail(
        EmailSchema(
            sub="Verify email",
            email_to=[user.email],
            body=dict(
                title="Verify Email",
                message="Hello %s, welcome to Pilearn<br>Please verify you email by clicking the link below." % user.full_name,
                link=verify_email_link,
                link_name="Verify"
            )
        )
    )
    response = SchemalessResponse(
        data=dict(
            success=True
        ),
        message="user created successfully"
    )
    return JSONResponse(jsonable_encoder(response))


@router.post('/login', response_model=SchemalessResponse)
async def user_login(login: UserLoginSchema = Body(...)):
    user = await MongoInterface.find_or_404(
        collections['users'],
        query=dict(
            email=login.user_email
        ),
        exclude=dict(
            passwd=1
        )
    )
    if not verify_password(login.passwd, user['passwd']):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Invalid Password")
    user_token = await create_access_token(
        data=dict(
            user_id=str(user['_id'])
        ),
        expires_delta=timedelta(days=5)
    )
    response = SchemalessResponse(
        data=dict(
            token=user_token,
            success=True
        ),
        message="user logged in"
    )
    return JSONResponse(jsonable_encoder(response))


@router.get('/user_verification', response_model=SchemalessResponse)
async def user_verify(verify_user: str):
    user, payload = await verify_token(verify_user, key=Config.JWT_EMAIL_SECRET)
    update_doc = await MongoInterface.update_doc(
        collection_name=collections['users'],
        query=dict(
            _id=ObjectId(payload.get("user_id"))
        ),
        update_data=dict(
            disabled=False,
            is_verified=True,
        ),
        q_type="set"
    )

    response = SchemalessResponse(
        data=dict(
            login_link=Config.HOST_URL+"users/login",
            success=True
        ),
        message="User Verified"
    )

    return JSONResponse(jsonable_encoder(response))
