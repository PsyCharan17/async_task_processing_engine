from pydantic import BaseModel
from typing import Optional

class JobCreate(BaseModel):
    input_data:dict 

class JobResponse(BaseModel):
    id: str
    status: str
    input_data: dict
    result: Optional[dict] = None