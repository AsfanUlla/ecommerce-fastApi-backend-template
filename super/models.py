from pydantic import BaseModel, Field, EmailStr
from fastapi import Header
from typing import Optional, List, Dict


class UserUpdateData(BaseModel):
    disabled: bool = True
    is_verified: bool = False
    is_teacher: bool = False
    is_admin: bool = False
    is_su_admin: bool = False
