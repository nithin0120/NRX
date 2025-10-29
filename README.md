# Neural Remix Engine (NRX)

An AI-powered multi-model platform for intelligent music transformation across genres while preserving the original song's identity.

**Not just a MusicGen wrapper** - NRX orchestrates multiple AI subsystems (Demucs v4, Librosa, MusicGen Melody) to create a production-grade music transformation engine with smart vocal synchronization.

## Live Demo

- **Frontend**: http://localhost:3000
- **Backend API**: http://localhost:8000
- **API Docs**: http://localhost:8000/docs

## Key Features

### Core Capabilities
- **AI Stem Separation** - Demucs v4 (htdemucs) isolates vocals, drums, bass, and accompaniment
- **Musical Analysis** - Librosa extracts tempo, key, chord structure, energy, and brightness
- **Style Transfer** - 8 preset genres (Lofi, Synthwave, Neo-Soul, Acoustic, EDM, Jazz, Rock, Orchestral)
- **Conditional Generation** - MusicGen Melody transforms instrumentals while preserving structure
- **Smart Vocal Sync** - Automatically matches vocals to AI-generated tempo with intelligent pitch adjustment
- **Real-time Progress** - Async job processing with detailed stage-by-stage updates

### What Makes NRX Different

| Aspect | Typical MusicGen Usage | NRX Platform |
|--------|------------------------|--------------|
| **Input** | Text prompt or simple melody | Full audio file + musical context |
| **Processing** | Single model inference | 3 AI subsystems orchestrated |
| **Output** | New song from scratch | Transformed version of YOUR song |
| **Identity** | No preservation | Original song recognizable |
| **Control** | Text description only | Musical analysis + style presets + parameter tuning |
| **Vocals** | Not handled | Smart sync with automatic tempo/pitch matching |
| **Use Case** | "Generate lofi music" | "Transform THIS song to lofi" |

## Quick Start

### Prerequisites

- Python 3.10
- Node.js 16+
- Redis

### Installation

1. **Clone and setup environment:**
```bash
git clone https://github.com/nithin0120/NRX.git
cd NRX
python3.10 -m venv venv
source venv/bin/activate
```

2. **Install dependencies:**
```bash
# Install core dependencies
pip install -r requirements-core.txt

# Install ML dependencies (may take a while)
pip install -r requirements-ml.txt
```

3. **Install and start Redis:**
```bash
brew install redis  # macOS
brew services start redis
```

4. **Start the backend services:**
```bash
# Terminal 1: FastAPI backend
python -m backend.main

# Terminal 2: Celery worker
celery -A backend.tasks worker --loglevel=info
```

5. **Install and run frontend:**
```bash
cd frontend
npm install
npm start
```

The app will be available at http://localhost:3000

### First Run

When you first generate a remix:
- Demucs model (~200MB) will download
- MusicGen model (~1.5GB) will download
- Processing takes 5-7 minutes for a 30-second clip

Subsequent remixes are faster as models are cached.

## How to Use

1. **Upload** - Drop an audio file (MP3, WAV, FLAC, M4A)
2. **Select Genre** - Choose from 8 preset styles
3. **Adjust Parameters**:
   - **Energy** (0.5-2.0): Controls intensity and power
   - **Brightness** (0.5-2.0): Controls high-frequency clarity
4. **Generate** - Click to start remix job
5. **Wait** - Progress updates show each processing stage
6. **Download** - Listen and download your remix

## Architecture

### System Design

```
┌─────────────┐     ┌──────────────┐     ┌─────────────┐
│   Frontend  │────▶│  FastAPI     │────▶│   Redis     │
│   (React)   │     │   Backend    │     │   Queue     │
└─────────────┘     └──────────────┘     └─────────────┘
                           │
                           ▼
                    ┌──────────────┐
                    │    Celery    │
                    │    Worker    │
                    └──────────────┘
                           │
                           ▼
                    ┌──────────────┐
                    │ ML Pipeline  │
                    └──────────────┘
```

### Multi-Model Pipeline

```
┌──────────────────────────────────────────────────────────┐
│                   Neural Remix Engine                     │
└──────────────────────────────────────────────────────────┘
                           │
        ┌──────────────────┼──────────────────┐
        │                  │                  │
        ▼                  ▼                  ▼
┌──────────────┐   ┌──────────────┐   ┌──────────────┐
│  Demucs v4   │   │  Librosa     │   │  MusicGen    │
│  Separation  │   │  Analysis    │   │  Generation  │
└──────────────┘   └──────────────┘   └──────────────┘
        │                  │                  │
        └──────────────────┼──────────────────┘
                           │
                           ▼
                  ┌─────────────────┐
                  │  Smart Vocal    │
                  │  Sync + Mixing  │
                  └─────────────────┘
                           │
                           ▼
                    [Final Remix]
```

### Processing Pipeline

1. **Input Processing (Demucs)**
   - Separates audio into 4 stems: vocals, drums, bass, other
   - Uses state-of-the-art hybrid transformer model
   - Trained on MUSDB18-HQ dataset

2. **Musical Analysis (Librosa)**
   - Tempo detection (BPM)
   - Key and chord estimation
   - Spectral analysis (brightness, energy)
   - Beat tracking

3. **Style Mapping**
   - Genre-aware text prompts for MusicGen
   - Combines analyzed features with user parameters
   - Incorporates tempo, key, energy, brightness

4. **Conditional Generation (MusicGen Melody)**
   - Audio-conditional generation (not just text-to-music)
   - Preserves melodic structure from instrumental stems
   - Transforms style while maintaining timing

5. **Smart Vocal Sync**
   - Analyzes ACTUAL tempo of generated instrumental
   - Matches vocals to real output (not theoretical)
   - Intelligent pitch adjustment for large tempo changes
   - Sample rate matching (44.1kHz → 32kHz)
   - Phase vocoder time-stretching for quality

6. **Post-Processing & Mixing**
   - Blends processed vocals with generated instrumental
   - Adaptive mixing based on genre characteristics
   - Normalization and final mastering

## Smart Vocal Sync

### The Problem We Solved

Traditional approaches would guess a target tempo and adjust vocals accordingly. But AI generators are unpredictable - MusicGen might create music at 95 BPM when you expected 100 BPM, causing vocals to drift out of sync.

### Our Solution

**Match vocals to the ACTUAL generated instrumental:**

1. Generate AI instrumental first
2. Analyze what was actually created (e.g., 95.3 BPM)
3. Adjust vocals to match that specific tempo precisely
4. Apply intelligent pitch adjustment for naturalness
5. Blend perfectly synchronized audio

### Result

Vocals that lock perfectly with the beat, every time. No guessing, no theoretical targets, just perfect synchronization.

### Example

```
Original song: 126 BPM
Target genre: Neo-Soul

Step 1: Generate instrumental with MusicGen
Step 2: Analyze actual output → 95.3 BPM
Step 3: Adjust vocals: 126.0 → 95.3 BPM
Step 4: Lower pitch by 0.5 semitones (for slower tempo)
Step 5: Resample: 44100 Hz → 32000 Hz
Step 6: Blend vocals (95.3 BPM) with instrumental (95.3 BPM)

Result: Perfect sync! ✓
```

## API Endpoints

### Upload Track
```
POST /api/upload
Content-Type: multipart/form-data

Request:
- file: audio file (mp3, wav, flac, m4a)

Response:
{
  "file_id": "uuid",
  "filename": "song.mp3",
  "duration": 180.5,
  "message": "File uploaded successfully"
}
```

### Start Remix Job
```
POST /api/remix
Content-Type: application/json

Request:
{
  "file_id": "uuid",
  "style": "lofi_chill",
  "energy": 1.0,
  "brightness": 1.0
}

Response:
{
  "job_id": "uuid",
  "status": "processing",
  "message": "Remix job started"
}
```

### Check Job Status
```
GET /api/status/{job_id}

Response:
{
  "job_id": "uuid",
  "status": "completed",
  "progress": 100,
  "result": {
    "output_path": "outputs/remix_xxx.wav",
    "analysis": {...},
    "model": "MusicGen (via Transformers)",
    "mode": "full"
  }
}
```

### Download Remix
```
GET /api/download/{job_id}

Response: Audio file stream
```

### Get Available Styles
```
GET /api/styles

Response:
{
  "styles": [
    {
      "id": "lofi_chill",
      "name": "Lofi Chill",
      "description": "Relaxed lo-fi hip hop beats",
      "tempo_range": [70, 90],
      "energy": 0.4
    },
    ...
  ]
}
```

### System Info
```
GET /api/system

Response:
{
  "mode": "full",
  "models": {
    "demucs": "active",
    "librosa": "active",
    "musicgen": "active"
  }
}
```

## Available Genres

| Style | Description | Tempo Range | Energy |
|-------|-------------|-------------|--------|
| **Lofi Chill** | Relaxed hip hop beats with vinyl warmth | 70-90 BPM | 0.4 |
| **Synthwave** | 80s retro synthesizers with neon vibes | 100-130 BPM | 0.7 |
| **Neo-Soul** | Smooth R&B with complex harmonies | 80-110 BPM | 0.6 |
| **Acoustic** | Organic guitar-based folk sound | 80-120 BPM | 0.5 |
| **EDM** | High-energy electronic with big drops | 120-140 BPM | 0.9 |
| **Jazz** | Sophisticated improvisation | 100-180 BPM | 0.6 |
| **Rock** | Electric guitar-driven anthems | 110-150 BPM | 0.8 |
| **Orchestral** | Cinematic sweeping arrangements | 60-120 BPM | 0.7 |

## Tech Stack

### Backend
- **FastAPI** - Modern async web framework
- **Celery** - Distributed task queue
- **Redis** - Job queue broker and result backend
- **PyTorch** - ML framework

### ML Models
- **Demucs v4** (htdemucs) - State-of-the-art source separation
- **Librosa** (v0.11) - Audio analysis and feature extraction
- **MusicGen Melody** (via Transformers) - Conditional audio generation
- **pyrubberband** - High-quality time/pitch manipulation

### Frontend
- **React** - UI framework
- **Axios** - HTTP client
- **Web Audio API** - Audio playback

### DevOps
- **Docker** & **Docker Compose** - Containerization
- **Git** - Version control

## Project Structure

```
NRX/
├── backend/
│   ├── api/
│   │   ├── routes.py          # FastAPI endpoints
│   │   └── models.py          # Pydantic schemas
│   ├── pipeline/
│   │   ├── separation.py      # Demucs stem separation
│   │   ├── analysis.py        # Librosa analysis
│   │   ├── generation_transformers.py  # MusicGen
│   │   ├── vocal_processing.py  # Smart vocal sync
│   │   └── processor_full.py  # Main pipeline
│   ├── utils/
│   │   └── audio.py           # Audio utilities
│   ├── config.py              # Configuration
│   ├── main.py                # FastAPI app
│   └── tasks.py               # Celery tasks
├── frontend/
│   ├── public/
│   └── src/
│       ├── components/
│       │   ├── AudioPlayer.js
│       │   ├── FileUpload.js
│       │   ├── ParameterControls.js
│       │   └── StatusDisplay.js
│       └── App.js
├── uploads/                   # Uploaded files (gitignored)
├── outputs/                   # Generated remixes (gitignored)
├── requirements-core.txt      # Core Python dependencies
├── requirements-ml.txt        # ML dependencies
├── Dockerfile
├── docker-compose.yml
└── README.md
```

## Troubleshooting

### Services Not Running

```bash
# Check if processes are running
ps aux | grep "backend.main"
ps aux | grep "celery"
ps aux | grep "npm"

# Restart services
pkill -f "python.*backend.main"
pkill -f "celery.*backend.tasks"
cd /Users/nithinparthasarathy/NRX
source venv/bin/activate
python -m backend.main &
celery -A backend.tasks worker --loglevel=info &
cd frontend && npm start
```

### Redis Connection Issues

```bash
# Check Redis status
brew services list

# Start Redis
brew services start redis

# Test connection
redis-cli ping  # Should return "PONG"
```

### Module Not Found Errors

```bash
# Activate virtual environment
source venv/bin/activate

# Reinstall dependencies
pip install -r requirements-core.txt
pip install -r requirements-ml.txt
```

### Slow First Remix

This is normal! The first remix downloads models:
- Demucs: ~200MB
- MusicGen: ~1.5GB

Models are cached in:
- `~/.cache/torch/hub/`
- `~/.cache/huggingface/`

Subsequent remixes are much faster (3-5 minutes for 30 seconds).

### Out of Memory

If you run out of memory during processing:

1. Use shorter audio clips (< 60 seconds)
2. Close other applications
3. Restart the Celery worker
4. Consider using GPU if available

## Development

### Running Tests

```bash
source venv/bin/activate
pytest tests/
```

### Linting

```bash
flake8 backend/
black backend/
```

### Adding New Genres

Edit `backend/pipeline/processor_full.py`:

```python
STYLE_PRESETS = {
    "your_genre": {
        "tempo_range": (80, 120),
        "energy": 0.6,
        "complexity": "medium",
        "description": "detailed genre description for MusicGen"
    }
}
```

## Deployment

### Docker

```bash
docker-compose up --build
```

### Production Considerations

- Use GPU for faster processing (update Dockerfile)
- Scale Celery workers horizontally
- Use persistent Redis storage
- Add authentication for API endpoints
- Implement rate limiting
- Set up monitoring (Prometheus, Grafana)
- Configure S3 for file storage

## Future Roadmap

### Phase 1: Advanced Style Understanding
- Integrate CLAP for semantic audio-text embeddings
- Add MERT for genre classification
- LLM layer for conversational style refinement

### Phase 2: Interactive Refinement
- Per-stem style control
- Iterative generation ("make it more energetic")
- Real-time preview during generation

### Phase 3: Multi-Genre Blending
- Latent space interpolation between styles
- Custom style creation from examples
- Style transfer learning from user favorites

### Phase 4: Production Features
- User authentication and accounts
- Cloud storage integration
- Batch processing
- API rate limiting
- Advanced error recovery
- Monitoring and analytics

### Phase 5: Collaboration
- Version control for remixes
- A/B testing framework
- Community style library
- Provenance tracking and watermarking

## Why This Project Stands Out

### For Resumes and Portfolios

**Instead of saying:** "Used MusicGen for music generation"

**You can say:** "Built NRX, a multi-model AI platform for intelligent music transformation"

### What This Demonstrates

1. **ML Systems Engineering**
   - Multi-model pipeline orchestration
   - Async job processing with Celery
   - Model versioning and caching

2. **Audio ML Expertise**
   - Source separation (Demucs)
   - Feature extraction (Librosa)
   - Conditional generation (MusicGen)
   - Advanced audio processing (phase vocoder, resampling)

3. **Software Architecture**
   - Microservices (API, Worker, Cache)
   - Job queue management
   - Real-time progress tracking
   - Error handling and retry logic

4. **Full-Stack Development**
   - Backend: FastAPI, Celery, Redis
   - Frontend: React with audio visualization
   - DevOps: Docker, Docker Compose

5. **Product Thinking**
   - User-centric design (smart vocal sync, progress updates)
   - Iterative improvement
   - Scalability considerations

### The Analogy

**NRX is to MusicGen what Photoshop is to a CNN image generator.**

MusicGen is the powerful engine underneath, but NRX is the complete application that makes it useful, controllable, and production-ready for real-world music transformation tasks.

## License

MIT License - see LICENSE file for details

## Credits

- **Demucs** - Meta AI Research
- **Librosa** - librosa.org
- **MusicGen** - Meta AudioCraft
- **pyrubberband** - Rubber Band Audio Time Stretcher

## Contributing

Contributions are welcome! Please open an issue or submit a pull request.

## Contact

GitHub: [@nithin0120](https://github.com/nithin0120)

---

**Built with ❤️ for music lovers and AI enthusiasts**
