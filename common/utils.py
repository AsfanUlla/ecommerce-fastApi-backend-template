from fastapi import HTTPException, status, BackgroundTasks, Depends
from passlib.context import CryptContext
from datetime import datetime, timedelta
from typing import Optional, Dict
from jose import JWTError, jwt
from config import Config
from common.db import collections
from common.views import MongoInterface
from bson import ObjectId
from fastapi_mail import FastMail, MessageSchema
from fastapi_mail import ConnectionConfig
from pydantic import EmailStr
from common.models import EmailSchema

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
ALGORITHM = "HS256"

mail_conf = ConnectionConfig(
    MAIL_USERNAME="tech@pi-learn.online",
    MAIL_PASSWORD="p1l34rnt34ch!",
    MAIL_FROM="tech@pi-learn.online",
    MAIL_PORT=465,
    MAIL_SERVER="mail.pi-learn.online",
    MAIL_FROM_NAME="Pilearn",
    MAIL_TLS=False,
    MAIL_SSL=True,
    TEMPLATE_FOLDER='./templates/email'
)

mail = FastMail(mail_conf)


def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password):
    return pwd_context.hash(password)


async def create_access_token(data: dict, expires_delta: Optional[timedelta] = None, key: str = Config.JWT_SECRET_KEY):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=30)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, key, algorithm=ALGORITHM)
    return encoded_jwt


async def verify_token(token, key: str = Config.JWT_SECRET_KEY):
    try:
        payload = jwt.decode(token, key, algorithms=[ALGORITHM])
        user_id: str = payload.get("user_id")
        if user_id is None:
            raise HTTPException(status.HTTP_401_UNAUTHORIZED, detail="Illegal token")
        user = await MongoInterface.find_or_404(
            collections['users'],
            query=dict(
                _id=ObjectId(user_id),
            ),
            exclude=dict(
                _id=False,
                cd=False
            ),
            error_message="Illegal token"
        )
    except JWTError:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, detail="Illegal token")
    return user, payload


async def send_mail(data: EmailSchema):
    message = MessageSchema(
        subject=data.sub,
        recipients=data.email_to,
        template_body=data.dict().get('body'),
        subtype='html',
    )
    await mail.send_message(message, template_name=data.template_name)
