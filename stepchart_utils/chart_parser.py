import re
from pathlib import Path
from typing import List
import logging

from stepchart_utils.ssc_file import SSCFile
from stepchart_utils.step_chart_file import StepChartFile

from .sm_file import SMFile

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


class Chart:
    def __init__(self, chart_file: StepChartFile, video_file: Path, audio_file: Path):
        self.chart_file = chart_file
        self.video_file = video_file
        self.audio_file = audio_file

    def validate(self):
        self.chart_file.validate()
        if self.video_file and not self.video_file.exists():
            raise FileNotFoundError(f"Video file {self.video_file} does not exist")
        if self.audio_file and not self.audio_file.exists():
            raise FileNotFoundError(f"Audio file {self.audio_file} does not exist")


class ChartParser:
    def __init__(self):
        pass

    def parse_file(self, filepath: Path) -> Chart:
        if filepath.suffix == ".sm":
            return self.parse_sm_file(filepath)
        elif filepath.suffix == ".ssc":
            return self.parse_ssc_file(filepath)
        else:
            raise ValueError(f"Unsupported file type: {filepath.suffix}")

    def parse_sm_file(self, filepath: Path) -> Chart:
        """Parse an SM file and return an SMFile object"""
        sm_file, audio_file, video_file = SMFile().parse(filepath)
        chart = Chart(sm_file, video_file, audio_file)

        return chart

    def parse_ssc_file(self, filepath: Path) -> Chart:
        """Parse an SSC file and return an SSCFile object"""
        ssc_file, audio_file, video_file = SSCFile().parse(filepath)
        chart = Chart(ssc_file, video_file, audio_file)

        return chart

    def is_chart_file(self, filepath: Path) -> bool:
        """Check if a file is a chart file"""
        return filepath.suffix in [".sm", ".ssc"]

    def get_chart_files_from_directory(self, directory: Path) -> List[Path]:
        """Return each chart file in a directory, recursively"""
        chart_files = []
        for file in directory.iterdir():
            if file.is_dir():
                chart_files.extend(self.get_chart_files_from_directory(file))
            elif self.is_chart_file(file):
                chart_files.append(file)

        return chart_files
