import librosa
import numpy as np
from pathlib import Path

class MusicAnalyzer:
    def __init__(self, sr: int = 44100):
        self.sr = sr
        
    def analyze(self, audio_path: Path):
        y, sr = librosa.load(audio_path, sr=self.sr)
        
        tempo, beats = librosa.beat.beat_track(y=y, sr=sr)
        
        chroma = librosa.feature.chroma_cqt(y=y, sr=sr)
        key = self._estimate_key(chroma)
        
        chords = self._estimate_chords(chroma)
        
        spectral_centroid = librosa.feature.spectral_centroid(y=y, sr=sr)
        brightness = float(np.mean(spectral_centroid))
        
        rms = librosa.feature.rms(y=y)
        energy = float(np.mean(rms))
        
        return {
            "tempo": float(tempo),
            "key": key,
            "chords": chords,
            "brightness": brightness,
            "energy": energy,
            "duration": len(y) / sr
        }
    
    def _estimate_key(self, chroma):
        key_names = ['C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#', 'A', 'A#', 'B']
        chroma_mean = np.mean(chroma, axis=1)
        key_idx = np.argmax(chroma_mean)
        return key_names[key_idx]
    
    def _estimate_chords(self, chroma):
        chord_templates = self._get_chord_templates()
        chroma_frames = chroma.T
        
        chords = []
        for frame in chroma_frames[::100]:
            similarities = []
            for template in chord_templates:
                similarity = np.dot(frame, template) / (np.linalg.norm(frame) * np.linalg.norm(template) + 1e-10)
                similarities.append(similarity)
            chords.append(np.argmax(similarities))
        
        return [int(c) for c in chords[:10]]
    
    def _get_chord_templates(self):
        major = np.array([1, 0, 0, 0, 1, 0, 0, 1, 0, 0, 0, 0])
        minor = np.array([1, 0, 0, 1, 0, 0, 0, 1, 0, 0, 0, 0])
        return [major, minor]

