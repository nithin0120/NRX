from pathlib import Path
import numpy as np
from backend.pipeline.separation import StemSeparator
from backend.pipeline.analysis import MusicAnalyzer
from backend.pipeline.generation import MusicGenerator
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

class RemixProcessor:
    def __init__(self):
        self.separator = StemSeparator()
        self.analyzer = MusicAnalyzer()
        self.generator = MusicGenerator()
        
    def process(self, audio_path: Path, style: str, energy: float = 1.0, brightness: float = 1.0):
        original_audio = load_audio(audio_path, sr=44100)
        
        analysis = self.analyzer.analyze(audio_path)
        
        stems = self.separator.separate(audio_path)
        
        style_description = self._build_description(style, analysis, energy, brightness)
        
        instrumental = self._combine_instrumental_stems(stems)
        
        duration = min(analysis["duration"], 30.0)
        
        remix = self.generator.generate_with_melody(
            melody_audio=instrumental,
            description=style_description,
            duration=duration
        )
        
        vocals = stems.get('vocals')
        if vocals is not None and vocals.shape[-1] > 0:
            remix = self._blend_with_vocals(remix, vocals, blend_ratio=0.7)
        
        remix = normalize_audio(remix)
        
        output_path = settings.output_dir / f"remix_{audio_path.stem}.wav"
        save_audio(remix, output_path, sr=self.generator.model.sample_rate)
        
        return {
            "output_path": str(output_path),
            "analysis": analysis,
            "style_description": style_description,
            "stems_used": list(stems.keys())
        }
    
    def _combine_instrumental_stems(self, stems: dict) -> np.ndarray:
        instrumental_keys = ['drums', 'bass', 'other']
        instrumental = None
        
        for key in instrumental_keys:
            if key in stems and stems[key] is not None:
                if instrumental is None:
                    instrumental = stems[key].copy()
                else:
                    min_length = min(instrumental.shape[-1], stems[key].shape[-1])
                    instrumental[..., :min_length] += stems[key][..., :min_length]
        
        if instrumental is None:
            instrumental = np.zeros((2, 44100))
        
        return instrumental
    
    def _blend_with_vocals(self, remix: np.ndarray, vocals: np.ndarray, blend_ratio: float = 0.7) -> np.ndarray:
        min_length = min(remix.shape[-1], vocals.shape[-1])
        
        if remix.shape[0] == 1 and vocals.shape[0] == 2:
            remix = np.repeat(remix, 2, axis=0)
        elif remix.shape[0] == 2 and vocals.shape[0] == 1:
            vocals = np.repeat(vocals, 2, axis=0)
        
        blended = np.zeros_like(remix)
        blended[..., :min_length] = remix[..., :min_length] * blend_ratio + vocals[..., :min_length] * (1 - blend_ratio)
        
        if min_length < remix.shape[-1]:
            blended[..., min_length:] = remix[..., min_length:]
        
        return blended
    
    def _build_description(self, style: str, analysis: dict, energy: float, brightness: float):
        base_style = STYLE_PRESETS.get(style, style)
        
        tempo_desc = "fast" if analysis["tempo"] > 120 else "slow" if analysis["tempo"] < 90 else "medium tempo"
        key_desc = f"in {analysis['key']}"
        
        energy_desc = "high energy" if energy > 1.2 else "low energy" if energy < 0.8 else ""
        brightness_desc = "bright" if brightness > 1.2 else "dark" if brightness < 0.8 else ""
        
        parts = [base_style, tempo_desc, key_desc, energy_desc, brightness_desc]
        return ", ".join([p for p in parts if p])

