import redis
import json
from backend.config import settings
from backend.api.models import JobStatus

redis_client = redis.Redis(
    host=settings.redis_host,
    port=settings.redis_port,
    decode_responses=True
)

def update_job_status(job_id: str, status: str, progress: int, result: dict = None, error: str = None):
    job_data = {
        "job_id": job_id,
        "status": status,
        "progress": progress,
        "result": result,
        "error": error
    }
    redis_client.setex(f"job:{job_id}", 3600, json.dumps(job_data))

def get_job_status(job_id: str) -> JobStatus | None:
    data = redis_client.get(f"job:{job_id}")
    if not data:
        return None
    
    job_data = json.loads(data)
    return JobStatus(**job_data)

