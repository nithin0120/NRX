from fastapi import APIRouter, UploadFile, File, HTTPException
from fastapi.responses import FileResponse
from pathlib import Path
import uuid
import shutil
from backend.api.models import RemixRequest, JobStatus, UploadResponse
from backend.config import settings
from backend.utils.audio import get_audio_info
from backend.tasks import process_remix_task
from backend.worker import get_job_status

router = APIRouter()

@router.post("/upload", response_model=UploadResponse)
async def upload_audio(file: UploadFile = File(...)):
    if not file.filename:
        raise HTTPException(status_code=400, detail="No file provided")
    
    file_ext = Path(file.filename).suffix.lower()
    if file_ext not in settings.allowed_formats:
        raise HTTPException(status_code=400, detail=f"Format not supported. Allowed: {settings.allowed_formats}")
    
    file_id = str(uuid.uuid4())
    file_path = settings.upload_dir / f"{file_id}{file_ext}"
    
    with file_path.open("wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
    
    try:
        info = get_audio_info(file_path)
    except Exception as e:
        file_path.unlink()
        raise HTTPException(status_code=400, detail=f"Invalid audio file: {str(e)}")
    
    return UploadResponse(
        file_id=file_id,
        filename=file.filename,
        duration=info["duration"],
        message="Upload successful"
    )

@router.post("/remix", response_model=JobStatus)
async def create_remix(request: RemixRequest):
    file_path = None
    for ext in settings.allowed_formats:
        candidate = settings.upload_dir / f"{request.file_id}{ext}"
        if candidate.exists():
            file_path = candidate
            break
    
    if not file_path:
        raise HTTPException(status_code=404, detail="File not found")
    
    job_id = str(uuid.uuid4())
    
    task = process_remix_task.delay(
        job_id=job_id,
        audio_path=str(file_path),
        style=request.style,
        energy=request.energy,
        brightness=request.brightness
    )
    
    return JobStatus(
        job_id=job_id,
        status="processing",
        progress=0
    )

@router.get("/status/{job_id}", response_model=JobStatus)
async def check_status(job_id: str):
    status = get_job_status(job_id)
    if not status:
        raise HTTPException(status_code=404, detail="Job not found")
    return status

@router.get("/download/{job_id}")
async def download_remix(job_id: str):
    status = get_job_status(job_id)
    
    if not status:
        raise HTTPException(status_code=404, detail="Job not found")
    
    if status.status != "completed":
        raise HTTPException(status_code=400, detail="Remix not ready")
    
    if not status.result or "output_path" not in status.result:
        raise HTTPException(status_code=500, detail="Output file not found")
    
    output_path = Path(status.result["output_path"])
    
    if not output_path.exists():
        raise HTTPException(status_code=404, detail="Output file missing")
    
    return FileResponse(
        path=output_path,
        media_type="audio/wav",
        filename=f"remix_{job_id}.wav"
    )

@router.get("/styles")
async def get_styles():
    try:
        from backend.pipeline.processor import STYLE_PRESETS
    except ImportError:
        from backend.pipeline.mock_pipeline import STYLE_PRESETS
    return {"styles": list(STYLE_PRESETS.keys())}

@router.get("/system")
async def get_system_info():
    try:
        from backend.pipeline.processor_full import RemixProcessor
        mode = "full"
    except ImportError:
        try:
            from backend.pipeline.processor_hybrid import HybridRemixProcessor
            mode = "hybrid"
        except ImportError:
            mode = "mock"
    
    demucs_status = "active" if mode in ["full", "hybrid"] else "mock"
    librosa_status = "active" if mode in ["full", "hybrid"] else "mock"
    musicgen_status = "active (via Transformers)" if mode == "full" else "unavailable" if mode == "hybrid" else "mock"
    
    return {
        "platform": "Neural Remix Engine (NRX)",
        "version": "1.0.0",
        "mode": mode,
        "description": "Multi-model AI platform for intelligent music transformation",
        "ai_subsystems": {
            "input_processing": {
                "model": "Demucs v4 (htdemucs)",
                "purpose": "Source separation - isolates vocals, drums, bass, other",
                "status": demucs_status
            },
            "analysis_engine": {
                "model": "Librosa v0.11",
                "purpose": "Musical analysis - tempo, key, chords, spectral features",
                "status": librosa_status
            },
            "generation_engine": {
                "model": "MusicGen Melody (Meta AudioCraft)",
                "purpose": "Audio-conditional generation - transforms style while preserving structure",
                "status": musicgen_status
            },
            "post_processing": {
                "model": "Custom mixing pipeline",
                "purpose": "Stem blending, vocal preservation, normalization",
                "status": "active"
            },
            "style_mapping": {
                "model": "Rule-based presets (future: CLAP/MERT)",
                "purpose": "Maps text descriptions to musical parameters",
                "status": "active"
            }
        },
        "capabilities": [
            "Preserves original song identity",
            "Transforms genre/style intelligently" if mode == "full" else "Adjusts stem levels intelligently",
            "Maintains vocal characteristics",
            "Adapts tempo and key awareness",
            "Per-stem processing and mixing"
        ],
        "distinction": "NRX is a platform orchestrating multiple AI models, not a single model wrapper",
        "note": "Running in FULL mode: All AI models active! MusicGen via Transformers (no xformers needed)" if mode == "full" else "Running in hybrid mode: Demucs + Librosa working. MusicGen unavailable" if mode == "hybrid" else None
    }

