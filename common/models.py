from pydantic import BaseModel, Field, EmailStr
from typing import Optional, List, Dict


class SchemalessResponse(BaseModel):
    data: Dict = {}
    status_code: int = 200
    message: Optional[str] = "Request Processed"
