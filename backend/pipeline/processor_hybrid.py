from pathlib import Path
import numpy as np
from backend.pipeline.separation import StemSeparator
from backend.pipeline.analysis import MusicAnalyzer
from backend.utils.audio import save_audio, normalize_audio, load_audio
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

class HybridRemixProcessor:
    def __init__(self):
        self.separator = StemSeparator()
        self.analyzer = MusicAnalyzer()
        
    def process(self, audio_path: Path, style: str, energy: float = 1.0, brightness: float = 1.0):
        original_audio = load_audio(audio_path, sr=44100)
        
        analysis = self.analyzer.analyze(audio_path)
        
        stems = self.separator.separate(audio_path)
        
        style_description = self._build_description(style, analysis, energy, brightness)
        
        remix = self._style_transfer_stems(stems, style, energy, brightness, analysis)
        
        remix = normalize_audio(remix)
        
        output_path = settings.output_dir / f"remix_{audio_path.stem}.wav"
        save_audio(remix, output_path, sr=44100)
        
        return {
            "output_path": str(output_path),
            "analysis": analysis,
            "style_description": style_description,
            "stems_used": list(stems.keys()),
            "mode": "hybrid",
            "note": "Using Demucs + Librosa. MusicGen unavailable (requires xformers)"
        }
    
    def _style_transfer_stems(self, stems: dict, style: str, energy: float, brightness: float, analysis: dict) -> np.ndarray:
        vocals = stems.get('vocals', np.zeros((2, 44100)))
        drums = stems.get('drums', np.zeros((2, 44100)))
        bass = stems.get('bass', np.zeros((2, 44100)))
        other = stems.get('other', np.zeros((2, 44100)))
        
        max_len = max(vocals.shape[-1], drums.shape[-1], bass.shape[-1], other.shape[-1])
        
        def pad_stem(stem, target_len):
            if stem.shape[-1] < target_len:
                padding = np.zeros((stem.shape[0], target_len - stem.shape[-1]))
                return np.concatenate([stem, padding], axis=-1)
            return stem[:, :target_len]
        
        vocals = pad_stem(vocals, max_len)
        drums = pad_stem(drums, max_len)
        bass = pad_stem(bass, max_len)
        other = pad_stem(other, max_len)
        
        drums_adjusted = drums * energy
        bass_adjusted = bass * (1.0 + (energy - 1.0) * 0.5)
        
        other_adjusted = other * brightness
        
        remix = vocals * 0.3 + drums_adjusted * 0.25 + bass_adjusted * 0.25 + other_adjusted * 0.2
        
        return remix
    
    def _build_description(self, style: str, analysis: dict, energy: float, brightness: float):
        base_style = STYLE_PRESETS.get(style, style)
        tempo_desc = "fast" if analysis["tempo"] > 120 else "slow" if analysis["tempo"] < 90 else "medium tempo"
        key_desc = f"in {analysis['key']}"
        energy_desc = "high energy" if energy > 1.2 else "low energy" if energy < 0.8 else ""
        brightness_desc = "bright" if brightness > 1.2 else "dark" if brightness < 0.8 else ""
        
        parts = [base_style, tempo_desc, key_desc, energy_desc, brightness_desc]
        return ", ".join([p for p in parts if p])

