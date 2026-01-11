from pydantic import BaseModel
from typing import Optional

class WorkRecord(BaseModel):
    person_id: str
    person_name: Optional[str] = None
    company_id: str
    company_name: Optional[str] = None
    role: Optional[str] = None
    event_time: Optional[str] = None  # ISO string recommended
