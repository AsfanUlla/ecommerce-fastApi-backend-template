from pydantic import BaseModel, Field, EmailStr
from typing import Optional


class AddUserSchema(BaseModel):
    full_name: str = Field(...)
    email: EmailStr = Field(...)
    passwd: str = Field(...)


class UserLoginSchema(BaseModel):
    user_email: EmailStr = Field(...)
    passwd: str = Field(...)
