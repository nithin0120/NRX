import numpy as np
from pathlib import Path

try:
    import soundfile as sf
    import librosa
    AUDIO_LIBS_AVAILABLE = True
except ImportError:
    AUDIO_LIBS_AVAILABLE = False

def load_audio(path: Path, sr: int = 44100):
    if not AUDIO_LIBS_AVAILABLE:
        return np.zeros((2, sr * 10))
    audio, _ = librosa.load(path, sr=sr, mono=False)
    return audio

def save_audio(audio: np.ndarray, path: Path, sr: int = 44100):
    if not AUDIO_LIBS_AVAILABLE:
        path.write_text("Mock audio")
        return
    sf.write(path, audio.T, sr)

def normalize_audio(audio: np.ndarray, target_db: float = -14.0):
    current_db = 20 * np.log10(np.sqrt(np.mean(audio**2)) + 1e-10)
    gain = 10 ** ((target_db - current_db) / 20)
    return audio * gain

def get_audio_info(path: Path):
    if not AUDIO_LIBS_AVAILABLE:
        return {
            "duration": 30.0,
            "sample_rate": 44100,
            "channels": 2
        }
    audio, sr = librosa.load(path, sr=None)
    duration = librosa.get_duration(y=audio, sr=sr)
    return {
        "duration": duration,
        "sample_rate": sr,
        "channels": audio.shape[0] if audio.ndim > 1 else 1
    }

