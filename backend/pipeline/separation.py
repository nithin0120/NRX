import torch
import torchaudio
from demucs.pretrained import get_model
from demucs.apply import apply_model
from pathlib import Path
from backend.config import settings

class StemSeparator:
    def __init__(self):
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        self.model = get_model(settings.demucs_model)
        self.model.to(self.device)
        
    def separate(self, audio_path: Path):
        wav, sr = torchaudio.load(audio_path)
        
        if sr != self.model.samplerate:
            wav = torchaudio.functional.resample(wav, sr, self.model.samplerate)
        
        wav = wav.to(self.device)
        ref = wav.mean(0)
        wav = (wav - ref.mean()) / ref.std()
        
        with torch.no_grad():
            sources = apply_model(self.model, wav[None], device=self.device)[0]
        
        sources = sources * ref.std() + ref.mean()
        
        stem_names = ["drums", "bass", "other", "vocals"]
        stems = {}
        
        for i, name in enumerate(stem_names):
            stems[name] = sources[i].cpu().numpy()
            
        return stems

