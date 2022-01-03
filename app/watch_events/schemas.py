import uuid
from pydantic import BaseModel
from typing import Optional


class WatchEventSchema(BaseModel):
    host_id: str
    start_time: float
    end_time: float
    duration: float
    complete: bool
    path: Optional[str]