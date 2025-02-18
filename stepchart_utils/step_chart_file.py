from abc import ABC, abstractmethod


class StepChartFile(ABC):
    @abstractmethod
    def parse(self) -> None:
        """Parse the file contents into structured data"""
        pass

    @abstractmethod
    def validate(self) -> None:
        """Validate the parsed data against format specifications"""
        pass
