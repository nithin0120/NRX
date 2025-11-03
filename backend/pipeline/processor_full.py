from pathlib import Path
import numpy as np
from backend.pipeline.separation import StemSeparator
from backend.pipeline.analysis import MusicAnalyzer
from backend.pipeline.generation_transformers import MusicGenerator
from backend.pipeline.vocal_processing import VocalProcessor
from backend.utils.audio import save_audio, normalize_audio, load_audio
from backend.config import settings

STYLE_PRESETS = {
    "lofi_chill": "lofi hip hop, chill beats, mellow jazz chords, vinyl crackle, relaxed atmosphere, smooth bass",
    "synthwave": "synthwave 80s, retro synthesizers, neon aesthetic, electronic drums, nostalgic melodies, spacey pads",
    "neo_soul": "neo soul, smooth rnb, warm electric piano, deep bass grooves, soulful atmosphere, jazz harmonies",
    "acoustic": "acoustic guitar, organic instrumentation, natural sound, unplugged, intimate performance, folk elements",
    "edm": "electronic dance music, festival banger, energetic drops, uplifting melodies, euphoric synths, big room sound",
    "jazz": "jazz music, sophisticated harmonies, swing rhythm, improvisation, brass section, walking bass, bebop influences",
    "rock": "rock music, electric guitars with distortion, powerful drums, energetic performance, anthemic sound, band arrangement",
    "orchestral": "orchestral cinematic, epic strings, brass fanfares, dramatic percussion, sweeping melodies, film score atmosphere"
}

GENRE_CHARACTERISTICS = {
    "lofi_chill": {
        "tempo_range": (70, 90),
        "energy": 0.4,
        "complexity": "simple",
        "description": "Laid-back hip-hop influenced beats with jazz elements"
    },
    "synthwave": {
        "tempo_range": (100, 130),
        "energy": 0.7,
        "complexity": "medium",
        "description": "80s-inspired electronic music with retro synthesizers"
    },
    "neo_soul": {
        "tempo_range": (80, 100),
        "energy": 0.6,
        "complexity": "complex",
        "description": "Contemporary R&B with jazz and soul influences"
    },
    "acoustic": {
        "tempo_range": (80, 120),
        "energy": 0.5,
        "complexity": "simple",
        "description": "Organic instruments, primarily guitar-based"
    },
    "edm": {
        "tempo_range": (120, 140),
        "energy": 0.9,
        "complexity": "medium",
        "description": "High-energy electronic dance music with big drops"
    },
    "jazz": {
        "tempo_range": (100, 180),
        "energy": 0.6,
        "complexity": "complex",
        "description": "Sophisticated harmonies with improvisation"
    },
    "rock": {
        "tempo_range": (110, 150),
        "energy": 0.8,
        "complexity": "medium",
        "description": "Electric guitar-driven energetic music"
    },
    "orchestral": {
        "tempo_range": (60, 120),
        "energy": 0.7,
        "complexity": "complex",
        "description": "Cinematic orchestral arrangements"
    }
}

class RemixProcessor:
    def __init__(self):
        self.separator = StemSeparator()
        self.analyzer = MusicAnalyzer()
        self.generator = MusicGenerator()
        self.vocal_processor = VocalProcessor()
        
    def process(self, audio_path: Path, style: str, energy: float = 1.0, brightness: float = 1.0):
        original_audio = load_audio(audio_path, sr=44100)
        
        print(f"Step 1: Analyzing musical structure...")
        analysis = self.analyzer.analyze(audio_path)
        
        print(f"Step 2: Separating stems with Demucs v4...")
        stems = self.separator.separate(audio_path)
        
        print(f"Step 3: Building genre-aware description...")
        style_description = self._build_genre_aware_description(
            style, analysis, energy, brightness
        )
        
        print(f"Step 4: Generating {style} version with MusicGen...")
        print(f"   Prompt: {style_description}")
        
        duration = min(analysis["duration"], 30.0)
        
        instrumental = self._combine_instrumental_stems(stems)
        
        remix = self.generator.generate_with_conditioning(
            melody_audio=instrumental,
            description=style_description,
            duration=duration
        )
        
        print(f"Step 5: Analyzing AI-generated instrumental...")
        vocals = stems.get('vocals')
        if vocals is not None and vocals.shape[-1] > 0:
            # Analyze what MusicGen actually created
            import librosa as lb
            
            # MusicGen generates at 32kHz, analyze that
            generated_tempo = lb.beat.tempo(y=remix[0] if remix.ndim > 1 else remix, sr=self.generator.sample_rate)[0]
            
            print(f"   Original vocals: {analysis['tempo']:.1f} BPM")
            print(f"   AI-generated instrumental: {generated_tempo:.1f} BPM")
            
            # Calculate how much to adjust vocals to match the actual generated output
            tempo_diff = abs(generated_tempo - analysis["tempo"])
            
            if tempo_diff > 5.0:
                print(f"   Matching vocals to AI-generated tempo...")
                print(f"   - Adjusting: {analysis['tempo']:.1f} → {generated_tempo:.1f} BPM")
                
                # Determine if we need pitch adjustment based on the tempo change
                tempo_ratio = generated_tempo / analysis["tempo"]
                pitch_adjustment = 0.0
                
                # For significant tempo changes, adjust pitch slightly to maintain vocal character
                if tempo_ratio < 0.85:  # Slowing down significantly
                    pitch_adjustment = -0.5
                    print(f"   - Lowering pitch by 0.5 semitones for slower tempo")
                elif tempo_ratio > 1.15:  # Speeding up significantly
                    pitch_adjustment = +0.5
                    print(f"   - Raising pitch by 0.5 semitones for faster tempo")
                
                # Resample vocals to match MusicGen's sample rate first
                if self.generator.sample_rate != 44100:
                    print(f"   Resampling vocals: 44100 → {self.generator.sample_rate} Hz")
                    vocals = lb.resample(
                        vocals, 
                        orig_sr=44100, 
                        target_sr=self.generator.sample_rate
                    )
                    if vocals.ndim == 1:
                        vocals = np.expand_dims(vocals, axis=0)
                
                # Now adjust to match the generated tempo
                vocals = self.vocal_processor.adjust_vocals_for_genre(
                    vocals=vocals,
                    original_tempo=analysis["tempo"],
                    target_tempo=generated_tempo,  # Match actual MusicGen output
                    pitch_shift_semitones=pitch_adjustment,
                    preserve_formants=True,
                    sample_rate=self.generator.sample_rate
                )
                print(f"   ✓ Vocals matched to AI-generated instrumental")
            else:
                print(f"   Tempos already aligned (within 5 BPM)")
                
                # Still need to resample to match MusicGen's sample rate
                if self.generator.sample_rate != 44100:
                    print(f"   Resampling vocals: 44100 → {self.generator.sample_rate} Hz")
                    vocals = lb.resample(
                        vocals, 
                        orig_sr=44100, 
                        target_sr=self.generator.sample_rate
                    )
                    if vocals.ndim == 1:
                        vocals = np.expand_dims(vocals, axis=0)
            
            remix = self._blend_with_vocals(remix, vocals, blend_ratio=0.65)
        
        remix = normalize_audio(remix)
        
        output_path = settings.output_dir / f"remix_{audio_path.stem}_{style}.wav"
        save_audio(remix, output_path, sr=self.generator.sample_rate)
        
        return {
            "output_path": str(output_path),
            "analysis": analysis,
            "style_description": style_description,
            "stems_used": list(stems.keys()),
            "mode": "full",
            "model": "MusicGen (via Transformers)",
            "genre_characteristics": GENRE_CHARACTERISTICS.get(style, {})
        }
    
    def _build_genre_aware_description(self, style: str, analysis: dict, energy: float, brightness: float):
        """
        Build a detailed genre-aware description for MusicGen.
        
        MusicGen was trained on 20,000 hours of music across many genres.
        The key to good genre transformation is detailed, specific prompts.
        """
        base_style = STYLE_PRESETS.get(style, style)
        genre_info = GENRE_CHARACTERISTICS.get(style, {})
        
        tempo = analysis["tempo"]
        key = analysis["key"]
        
        tempo_adjustment = ""
        if genre_info and "tempo_range" in genre_info:
            min_t, max_t = genre_info["tempo_range"]
            if tempo < min_t:
                tempo_adjustment = f"upbeat {int((min_t + max_t) / 2)} BPM"
            elif tempo > max_t:
                tempo_adjustment = f"moderate {int((min_t + max_t) / 2)} BPM"
            else:
                tempo_adjustment = f"{int(tempo)} BPM"
        
        energy_desc = ""
        if energy > 1.2:
            energy_desc = "high energy, powerful, intense"
        elif energy < 0.8:
            energy_desc = "low energy, calm, subdued"
        
        brightness_desc = ""
        if brightness > 1.2:
            brightness_desc = "bright, clear highs, crisp sound"
        elif brightness < 0.8:
            brightness_desc = "warm, dark, mellow tones"
        
        parts = [
            base_style,
            tempo_adjustment,
            f"in {key}",
            energy_desc,
            brightness_desc,
            "high quality production"
        ]
        
        description = ", ".join([p for p in parts if p])
        
        return description
    
    def _combine_instrumental_stems(self, stems: dict) -> np.ndarray:
        """Combine instrumental stems (drums, bass, other) for melody conditioning"""
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
    
    def _get_genre_vocal_pitch(self, style: str, original_tempo: float, target_tempo: float) -> float:
        """
        Intelligently determine pitch adjustment based on genre and tempo change.
        Returns pitch shift in semitones to make vocals match the genre vibe.
        """
        # Genre-specific vocal character adjustments
        genre_pitch_map = {
            'lofi_chill': -1.0,      # Lower, more relaxed vibe
            'neo_soul': -0.5,         # Slightly lower, smooth
            'synthwave': 0.0,         # Keep natural, retro feel
            'edm': +0.5,              # Slightly higher, energetic
            'rock': 0.0,              # Keep natural, powerful
            'jazz': 0.0,              # Natural, expressive
            'acoustic': 0.0,          # Completely natural
            'orchestral': -0.5        # Slightly lower, more dramatic
        }
        
        base_pitch = genre_pitch_map.get(style, 0.0)
        
        # Adjust based on tempo change magnitude
        tempo_ratio = target_tempo / original_tempo
        
        # If slowing down significantly (making it more chill), lower pitch more
        if tempo_ratio < 0.8:  # Slowing down > 20%
            base_pitch -= 0.5
        # If speeding up significantly (making it more energetic), raise pitch
        elif tempo_ratio > 1.2:  # Speeding up > 20%
            base_pitch += 0.5
        
        # Clamp to reasonable range
        return max(-2.0, min(2.0, base_pitch))
    
    def _blend_with_vocals(self, remix: np.ndarray, vocals: np.ndarray, blend_ratio: float = 0.65) -> np.ndarray:
        """Blend generated instrumental with original vocals"""
        min_length = min(remix.shape[-1], vocals.shape[-1])
        
        if remix.ndim == 1:
            remix = np.expand_dims(remix, 0)
        if vocals.ndim == 1:
            vocals = np.expand_dims(vocals, 0)
        
        if remix.shape[0] == 1 and vocals.shape[0] == 2:
            remix = np.repeat(remix, 2, axis=0)
        elif remix.shape[0] == 2 and vocals.shape[0] == 1:
            vocals = np.repeat(vocals, 2, axis=0)
        
        blended = np.zeros_like(remix)
        blended[..., :min_length] = remix[..., :min_length] * blend_ratio + vocals[..., :min_length] * (1 - blend_ratio)
        
        if min_length < remix.shape[-1]:
            blended[..., min_length:] = remix[..., min_length:]
        
        return blended

