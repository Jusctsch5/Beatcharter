from librosa import load
from librosa.feature.rhythm import tempo
from librosa.beat import beat_track
from pathlib import Path
from numpy import float64
from numpy.typing import NDArray

from beatcharter.beatchart.audio_analysis.audio_analysis_wrapper import AudioAnalysisWrapper

class LibrosaWrapper(AudioAnalysisWrapper):
    def __init__(self):
        pass

    def calculate_bpm(self, path: Path) -> NDArray[float64]:
        y, sr = load(path)
        bpm = tempo(y=y, sr=sr)
        return bpm
    
    def get_beats(self, path: Path):
        y, sr = load(path)
        tempo, _ = beat_track(y=y, sr=sr)
        return tempo
