from pydantic import BaseModel, Field, EmailStr, HttpUrl
from fastapi import Header
from typing import Optional, List, Dict
from common.views import PyObjectId


class UserUpdateData(BaseModel):
    disabled: bool = True
    is_verified: bool = False
    is_teacher: bool = False
    is_admin: bool = False
    is_su_admin: bool = False


class AddAdmin(BaseModel):
    org_name: str
    org_image: Optional[HttpUrl] = None
    org_description: Optional[str] = None
    org_is_active: bool = True
    user_id: PyObjectId
