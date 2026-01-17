from abc import abstractmethod
from pathlib import Path
from numpy import float64
from numpy.typing import NDArray


class AudioAnalysisWrapper:
    def __init__(self):
        pass

    @abstractmethod
    def calculate_bpm(self, path: Path) -> NDArray[float64]:
        pass
