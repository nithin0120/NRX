from pydantic import BaseModel, Field
from typing import Optional

class RemixRequest(BaseModel):
    file_id: str
    style: str
    energy: float = Field(default=1.0, ge=0.5, le=2.0)
    brightness: float = Field(default=1.0, ge=0.5, le=2.0)

class JobStatus(BaseModel):
    job_id: str
    status: str
    progress: int = 0
    result: Optional[dict] = None
    error: Optional[str] = None

class UploadResponse(BaseModel):
    file_id: str
    filename: str
    duration: float
    message: str

