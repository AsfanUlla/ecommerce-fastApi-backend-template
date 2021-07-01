from fastapi import APIRouter, Body, HTTPException, status
from fastapi.responses import JSONResponse
from users.models import AddUserSchema, UserLoginSchema
from common.models import SchemalessResponse
from fastapi.encoders import jsonable_encoder
from common.views import MongoInterface
from common.utils import get_password_hash, verify_password, create_access_token
from datetime import timedelta

router = APIRouter()


@router.post("/register", response_model=SchemalessResponse)
async def add_user(user: AddUserSchema = Body(..., )):
    user_doc = await MongoInterface.find_or_none(
        'users',
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
            is_staff=False,
            is_admin=False,
            is_su_admin=False,
        )
    )
    user_add = await MongoInterface.insert_one('users', post_obj)
    response = dict(
        data=dict(
            success=True
        ),
        message="user created successfully"
    )
    return JSONResponse(response)


@router.post('/login', response_model=SchemalessResponse)
async def user_login(login: UserLoginSchema = Body(...)):
    user = await MongoInterface.find_or_404(
        'users',
        query=dict(
            email=login.user_email
        ),
        exclude=dict(
            passwd=1
        )
    )
    if not verify_password(login.passwd, user['passwd']):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Invalid Password")
    user_token = create_access_token(
        data=dict(
            user_id=str(user['_id'])
        ),
        expires_delta=timedelta(days=5)
    )
    response = dict(
        data=dict(
            token=user_token,
            success=True
        ),
        message="user logged in"
    )
    return JSONResponse(response)
