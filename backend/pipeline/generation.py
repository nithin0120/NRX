import torch
from audiocraft.models import MusicGen
from backend.config import settings
import numpy as np

class MusicGenerator:
    def __init__(self):
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        self.model = MusicGen.get_pretrained('facebook/musicgen-melody', device=self.device)
        self.model.set_generation_params(duration=30)
        
    def generate(self, description: str, duration: float = 30.0, temperature: float = 1.0):
        self.model.set_generation_params(
            duration=duration,
            temperature=temperature,
            top_k=250,
            top_p=0.0,
        )
        
        wav = self.model.generate([description])
        audio = wav[0].cpu().numpy()
        
        return audio
    
    def generate_with_melody(self, melody_audio: np.ndarray, description: str, duration: float = 30.0):
        if len(melody_audio.shape) == 1:
            melody_audio = melody_audio.reshape(1, -1)
        elif melody_audio.shape[0] > 1:
            melody_audio = melody_audio.mean(axis=0, keepdims=True)
        
        melody_tensor = torch.from_numpy(melody_audio).float().to(self.device)
        
        if melody_tensor.dim() == 1:
            melody_tensor = melody_tensor.unsqueeze(0).unsqueeze(0)
        elif melody_tensor.dim() == 2:
            melody_tensor = melody_tensor.unsqueeze(0)
        
        self.model.set_generation_params(duration=duration)
        wav = self.model.generate_with_chroma(
            descriptions=[description],
            melody_wavs=melody_tensor,
            melody_sample_rate=self.model.sample_rate,
        )
        
        audio = wav[0].cpu().numpy()
        return audio
    
    def generate_continuation(self, prompt_audio: np.ndarray, description: str, duration: float = 30.0):
        prompt_tensor = torch.from_numpy(prompt_audio).float().unsqueeze(0).to(self.device)
        
        self.model.set_generation_params(duration=duration)
        wav = self.model.generate_continuation(prompt_tensor, prompt_sample_rate=self.model.sample_rate, descriptions=[description])
        
        audio = wav[0].cpu().numpy()
        return audio

