import numpy as np
import librosa
from typing import Optional

class VocalProcessor:
    """
    Processes vocals to match the target tempo and adjust pitch.
    Uses librosa's time stretching and pitch shifting.
    """
    
    def __init__(self):
        self.sr = 44100
    
    def adjust_vocals_for_genre(
        self,
        vocals: np.ndarray,
        original_tempo: float,
        target_tempo: float,
        pitch_shift_semitones: float = 0.0,
        preserve_formants: bool = True,
        sample_rate: int = 44100
    ) -> np.ndarray:
        """
        Adjust vocals to match the target tempo and optionally shift pitch.
        
        Args:
            vocals: Vocal audio array (channels, samples)
            original_tempo: Original song tempo in BPM
            target_tempo: Target genre tempo in BPM
            pitch_shift_semitones: Pitch shift in semitones (e.g., 2.0 = up 2 semitones)
            preserve_formants: If True, keeps vocal character when pitch shifting
            sample_rate: Sample rate of the vocal audio
            
        Returns:
            Processed vocal audio
        """
        self.sr = sample_rate  # Update to the actual sample rate being used
        
        # Calculate tempo change ratio
        tempo_ratio = target_tempo / original_tempo
        
        # If vocals are stereo, process each channel
        if len(vocals.shape) > 1 and vocals.shape[0] == 2:
            processed_left = self._process_mono_vocal(
                vocals[0], 
                tempo_ratio, 
                pitch_shift_semitones,
                preserve_formants
            )
            processed_right = self._process_mono_vocal(
                vocals[1], 
                tempo_ratio, 
                pitch_shift_semitones,
                preserve_formants
            )
            return np.stack([processed_left, processed_right])
        else:
            # Mono vocals
            if len(vocals.shape) > 1:
                vocals = vocals[0]
            processed = self._process_mono_vocal(
                vocals, 
                tempo_ratio, 
                pitch_shift_semitones,
                preserve_formants
            )
            return np.expand_dims(processed, axis=0)
    
    def _process_mono_vocal(
        self,
        vocal: np.ndarray,
        tempo_ratio: float,
        pitch_shift_semitones: float,
        preserve_formants: bool
    ) -> np.ndarray:
        """
        Process a mono vocal track.
        """
        # Step 1: Time stretch to match tempo
        # tempo_ratio < 1.0 = slow down
        # tempo_ratio > 1.0 = speed up
        if abs(tempo_ratio - 1.0) > 0.05:  # Only stretch if significant difference
            vocal = librosa.effects.time_stretch(vocal, rate=tempo_ratio)
        
        # Step 2: Pitch shift if requested
        if abs(pitch_shift_semitones) > 0.1:
            vocal = librosa.effects.pitch_shift(
                vocal,
                sr=self.sr,
                n_steps=pitch_shift_semitones
            )
        
        return vocal
    
    def estimate_optimal_pitch_shift(
        self,
        original_key: str,
        target_key: Optional[str] = None
    ) -> float:
        """
        Estimate optimal pitch shift to match target key.
        
        Args:
            original_key: Original song key (e.g., "G", "A minor")
            target_key: Target key (optional)
            
        Returns:
            Pitch shift in semitones
        """
        if not target_key:
            return 0.0
        
        # Key to semitone mapping (C = 0)
        key_map = {
            'C': 0, 'C#': 1, 'Db': 1, 'D': 2, 'D#': 3, 'Eb': 3,
            'E': 4, 'F': 5, 'F#': 6, 'Gb': 6, 'G': 7, 'G#': 8,
            'Ab': 8, 'A': 9, 'A#': 10, 'Bb': 10, 'B': 11
        }
        
        # Extract root note (ignore major/minor)
        orig_root = original_key.split()[0]
        target_root = target_key.split()[0]
        
        if orig_root in key_map and target_root in key_map:
            return key_map[target_root] - key_map[orig_root]
        
        return 0.0
    
    def get_genre_tempo_target(self, genre: str, original_tempo: float) -> float:
        """
        Get the optimal target tempo for a genre.
        
        Args:
            genre: Genre name
            original_tempo: Original song tempo
            
        Returns:
            Target tempo in BPM
        """
        genre_tempo_ranges = {
            'lofi_chill': (70, 90),
            'synthwave': (100, 120),
            'neo_soul': (80, 100),
            'acoustic': (80, 110),
            'edm': (120, 140),
            'jazz': (100, 160),
            'rock': (110, 140),
            'orchestral': (60, 100)
        }
        
        if genre not in genre_tempo_ranges:
            return original_tempo
        
        min_tempo, max_tempo = genre_tempo_ranges[genre]
        
        # If original is in range, keep it
        if min_tempo <= original_tempo <= max_tempo:
            return original_tempo
        
        # If too fast, slow to max of range
        if original_tempo > max_tempo:
            return max_tempo
        
        # If too slow, speed to min of range
        return min_tempo
    
    def normalize_vocals(self, vocals: np.ndarray, target_rms: float = 0.15) -> np.ndarray:
        """
        Normalize vocal loudness.
        
        Args:
            vocals: Vocal audio
            target_rms: Target RMS level
            
        Returns:
            Normalized vocals
        """
        current_rms = np.sqrt(np.mean(vocals ** 2))
        if current_rms > 0:
            vocals = vocals * (target_rms / current_rms)
        return vocals

