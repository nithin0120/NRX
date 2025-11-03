import torch
import numpy as np
from transformers import AutoProcessor, MusicgenForConditionalGeneration
from backend.config import settings

class MusicGenerator:
    def __init__(self):
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        print(f"Loading MusicGen model on {self.device}...")
        
        self.model = MusicgenForConditionalGeneration.from_pretrained('facebook/musicgen-small')
        self.processor = AutoProcessor.from_pretrained('facebook/musicgen-small')
        
        self.model = self.model.to(self.device)
        self.sample_rate = self.model.config.audio_encoder.sampling_rate
        
        print(f"✓ MusicGen loaded successfully (sample rate: {self.sample_rate}Hz)")
    
    def generate(self, description: str, duration: float = 30.0, temperature: float = 1.0):
        """Generate music from text description"""
        inputs = self.processor(
            text=[description],
            padding=True,
            return_tensors="pt",
        ).to(self.device)
        
        max_tokens = int(duration * 50)
        
        audio_values = self.model.generate(
            **inputs,
            max_new_tokens=max_tokens,
            do_sample=True,
            temperature=temperature,
            guidance_scale=3.0
        )
        
        audio = audio_values[0, 0].cpu().numpy()
        
        return audio
    
    def generate_with_conditioning(self, melody_audio: np.ndarray, description: str, duration: float = 30.0):
        """
        Generate music conditioned on input melody.
        
        Note: The base musicgen-small model doesn't have melody conditioning.
        For now, we use strong genre descriptions to guide the transformation.
        Future: Use musicgen-melody model when available in transformers.
        """
        if melody_audio.ndim == 2:
            melody_audio = melody_audio.mean(axis=0)
        
        enhanced_description = f"{description}, keeping the original melodic structure and rhythm"
        
        inputs = self.processor(
            text=[enhanced_description],
            padding=True,
            return_tensors="pt",
        ).to(self.device)
        
        max_tokens = int(duration * 50)
        
        audio_values = self.model.generate(
            **inputs,
            max_new_tokens=max_tokens,
            do_sample=True,
            temperature=0.9,
            guidance_scale=4.0
        )
        
        audio = audio_values[0, 0].cpu().numpy()
        
        return audio

