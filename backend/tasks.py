from celery import Celery
from pathlib import Path
from backend.config import settings
from backend.worker import update_job_status

try:
    from backend.pipeline.processor_full import RemixProcessor
    USE_REAL_ML = "full"
except ImportError:
    try:
        from backend.pipeline.processor_hybrid import HybridRemixProcessor as RemixProcessor
        USE_REAL_ML = "hybrid"
    except ImportError:
        from backend.pipeline.mock_pipeline import MockRemixProcessor as RemixProcessor
        USE_REAL_ML = "mock"

celery_app = Celery(
    "nrx",
    broker=f"redis://{settings.redis_host}:{settings.redis_port}/0",
    backend=f"redis://{settings.redis_host}:{settings.redis_port}/0"
)

@celery_app.task(bind=True)
def process_remix_task(self, job_id: str, audio_path: str, style: str, energy: float, brightness: float):
    try:
        update_job_status(job_id, "processing", 5, result={"stage": "Starting remix process"})
        
        processor = RemixProcessor()
        
        update_job_status(job_id, "processing", 15, result={"stage": "Analyzing audio structure"})
        
        update_job_status(job_id, "processing", 30, result={"stage": "Separating audio stems (this takes a moment)"})
        
        update_job_status(job_id, "processing", 55, result={"stage": "Generating remix with AI (this is the longest step)"})
        
        result = processor.process(
            audio_path=Path(audio_path),
            style=style,
            energy=energy,
            brightness=brightness
        )
        
        update_job_status(job_id, "processing", 90, result={"stage": "Finalizing and mixing"})
        
        result["mode"] = USE_REAL_ML
        
        update_job_status(job_id, "completed", 100, result=result)
        
        return result
        
    except Exception as e:
        error_msg = f"Error during remix: {str(e)}"
        update_job_status(job_id, "failed", 0, error=error_msg)
        raise

