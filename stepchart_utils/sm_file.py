from dataclasses import dataclass
from typing import List
from pathlib import Path


class FileMissing(Exception):
    def __init__(self, file_path: Path):
        self.file_path = file_path
        super().__init__(f"File {file_path} does not exist")

class FileUnspecified(Exception):
    def __init__(self, option: str):
        self.option = option
        super().__init__(f"File is not specified for option: #{option.upper()}:")

@dataclass
class SMFile:
    filepath: Path = None  # todo remove this and combine in Chart object, technically not SM
    title: str = ""
    subtitle: str = ""
    artist: str = ""
    genre: str = ""
    credit: str = ""
    menu_color: str = ""
    meter_type: str = ""
    banner: str = ""
    background: str = ""
    lyrics_path: str = ""
    jacket: str = ""
    cd_title: str = ""
    music: str = ""
    offset: float = 0.0
    sample_start: float = 0.0
    sample_length: float = 0.0
    selectable: str = "YES"
    list_sort: str = ""
    bpms: str = ""
    stops: str = ""
    bg_changes: str = ""
    bg_changes_beat: float = 0.0
    bg_changes_file: str = ""
    bg_changes_update_rate: float = 1.0
    bg_changes_crossfade: bool = False
    bg_changes_stretchrewind: bool = False
    bg_changes_stretchnoloop: bool = True
    bg_changes_effect: str = ""
    bg_changes_file2: str = ""
    bg_changes_transition: str = ""
    bg_changes_color1: str = ""
    bg_changes_color2: str = ""
    attacks: str = ""
    notes: List[str] = None

    def __post_init__(self):
        if self.notes is None:
            self.notes = []

    def validate(self):
        if self.filepath is None:
            raise ValueError("Filepath is required")
        if not self.filepath.exists():
            raise FileMissing(f"File {self.filepath} does not exist")
        
        chart_dir = self.filepath.parent

        # We want to have a jacket, banner, and background
        if not self.jacket:
            raise FileUnspecified("jacket")        
        if self.jacket and not (chart_dir / self.jacket).exists():
            raise FileMissing(f"Jacket file {self.jacket} does not exist")

        if not self.banner:
            raise FileUnspecified("banner")        
        if self.banner and not (chart_dir / self.banner).exists():
            raise FileMissing(f"Banner file {self.banner} does not exist")

        if not self.background:
            raise FileUnspecified("background")        
        if self.background and not (chart_dir / self.background).exists():
            raise FileMissing(f"Background file {self.background} does not exist")
        
        # Other things we do not care so much about
        if self.cd_title and not (chart_dir / self.cd_title).exists():
            raise FileMissing(f"CD title file {self.cd_title} does not exist")
        
        if self.lyrics_path and not (chart_dir / self.lyrics_path).exists():
            raise FileMissing(f"Lyrics file {self.lyrics_path} does not exist")
        


    