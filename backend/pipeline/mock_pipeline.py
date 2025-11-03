import time
import numpy as np
from pathlib import Path
from backend.config import settings

STYLE_PRESETS = {
    "lofi_chill": "lofi hip hop, chill beats, mellow, relaxed, jazzy chords, vinyl crackle",
    "synthwave": "synthwave, 80s synths, retro futuristic, neon, electronic, atmospheric",
    "neo_soul": "neo soul, smooth, rnb, warm electric piano, deep bass, soulful",
    "acoustic": "acoustic guitar, organic, natural, unplugged, intimate, singer songwriter",
    "edm": "electronic dance music, energetic, uplifting, festival, big drops, euphoric",
    "jazz": "jazz, sophisticated, swing, improvisational, brass section, walking bass",
    "rock": "rock music, electric guitars, drums, energetic, powerful, anthemic",
    "orchestral": "orchestral, cinematic, epic, strings, brass, dramatic, sweeping"
}

class MockRemixProcessor:
    def process(self, audio_path: Path, style: str, energy: float = 1.0, brightness: float = 1.0):
        time.sleep(2)
        
        analysis = {
            "tempo": 120.0,
            "key": "C",
            "chords": [0, 1, 0, 1],
            "brightness": 0.5 * brightness,
            "energy": 0.7 * energy,
            "duration": 30.0
        }
        
        style_description = self._build_description(style, analysis, energy, brightness)
        
        output_path = settings.output_dir / f"remix_{audio_path.stem}_mock.wav"
        
        sample_rate = 44100
        duration = 5
        frequency = 440
        t = np.linspace(0, duration, int(sample_rate * duration))
        audio = np.sin(2 * np.pi * frequency * t)
        
        try:
            import soundfile as sf
            sf.write(output_path, audio, sample_rate)
        except ImportError:
            output_path.write_text("Mock audio file")
        
        return {
            "output_path": str(output_path),
            "analysis": analysis,
            "style_description": style_description,
            "note": "This is a mock output. Install ML dependencies with: pip install -r requirements-ml.txt"
        }
    
    def _build_description(self, style: str, analysis: dict, energy: float, brightness: float):
        base_style = STYLE_PRESETS.get(style, style)
        tempo_desc = "fast" if analysis["tempo"] > 120 else "slow" if analysis["tempo"] < 90 else "medium tempo"
        key_desc = f"in {analysis['key']}"
        energy_desc = "high energy" if energy > 1.2 else "low energy" if energy < 0.8 else ""
        brightness_desc = "bright" if brightness > 1.2 else "dark" if brightness < 0.8 else ""
        
        parts = [base_style, tempo_desc, key_desc, energy_desc, brightness_desc]
        return ", ".join([p for p in parts if p])

