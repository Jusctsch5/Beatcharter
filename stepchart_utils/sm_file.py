from dataclasses import dataclass, field
from typing import List
from pathlib import Path
import logging

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

class ParseError(Exception):
    pass

class FileMissing(ParseError):
    def __init__(self, file_path: Path):
        self.file_path = file_path
        super().__init__(f"File {file_path} does not exist")

class FileUnspecified(ParseError):
    def __init__(self, option: str):
        self.option = option
        super().__init__(f"File is not specified for option: #{option.upper()}:")

class OptionWarning(ParseError):
    def __init__(self, option: str, message: str):
        self.option = option
        self.message = message
        super().__init__(f"Option warning for option: #{option.upper()}: {message}")


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
    bpms: list[tuple[float, float]]  = field(default_factory=list)
    stops: str = ""
    bg_changes: str = ""
    bg_changes_beat: float = 0.0
    bg_changes_file: str = ""
    bg_changes_update_rate: float = 1.0
    bg_changes_crossfade: bool = False
    bg_changes_stretchrewind: bool = False
    bg_changes_stretchnoloop: bool = False
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
        
        if self.offset != 0:
        
            # Let's calculate what the BGChanges beat should be
            # This is based off of the offset and the BPMs.
            # Lining up video, audio, and step chart. Assuming a case with no stepchart, where audio and video come from the same source, and you want to line them up as they are originally. However, if you have a non-zero OFFSET, you need to specify a non-zero start beat in order to sync the audio with the video. 
            # 
            # So the relation of the beat start of BGCHANGES (beats) to OFFSET (seconds) is complex because of the changes in units. This is predicated on BPMS. Take this example chart from BambooBladeOP:
            # 
            # #OFFSET:1.898;
            # #BPMS:0.000=160.002;
            # #BGCHANGES:5.000=BambooBladeOP.avi=1.000=1=0=0=StretchNoLoop==CrossFade==,
            # 240.000=BambooBladeOP-bg.png=1.000=1=0=0=StretchNoLoop==CrossFade==,
            # 99999.000=-nosongbg-=1.000=0=0=0=StretchNoLoop====
            # 
            # The #OFFSET is in seconds and #BGCHANGES=x=BambooBladeOP.avi, where x is referred to as "beat start" in beats.The exact number depends on the offset (#OFFSET), bpm of your song (#BPMS). 
            # A more programmatic way to calculate it is the following: 
            # 
            # offset (s) * bpm/60 (b/s) = beat offset
            # 
            # So plugging in Juzo's numbers above, 1.898 * 160.002/60 = 5.0613966 Which equates how one would come up with BGCHANGES:5.000

            logger.debug(f"Offset: {self.offset}")
            logger.debug(f"BPMs: {self.bpms}")
            bpm = self.bpms[0][1]
            calculated_bg_changes_beat = self.offset * bpm / 60
            calculated_bg_changes_beat = round(calculated_bg_changes_beat, 3)
            logger.debug(f"Calculated BGChanges beat: ~{calculated_bg_changes_beat}")

            # Check if the BGChanges beat is 0
            if self.bg_changes_beat == 0:
                raise OptionWarning("bg_changes", f"Offset is not zero ({self.offset}) but BGChanges beat is 0. Likely may see offset in audio/video. Calculated BGChanges beat: {calculated_bg_changes_beat}")

            # If the BGChanges beat is specified, but is off by >= 1.0, then we should warn
            if self.bg_changes_beat != calculated_bg_changes_beat:
                offset_diff = abs(self.bg_changes_beat - calculated_bg_changes_beat)
                if offset_diff >= 1.0:
                    raise OptionWarning("bg_changes", f"Offset is not zero ({self.offset}) but BGChanges beat is not equal to calculated BGChanges beat. Likely may see offset in audio/video. Calculated BGChanges beat: {calculated_bg_changes_beat}. Offset difference: {offset_diff}")

        if self.bg_changes_beat != 0:
            if self.bg_changes_file == "":
                raise OptionWarning("bg_changes", "BGChanges beat is present but BGChanges file is not specified")
            
            if self.bg_changes_stretchnoloop is False and "StretchNoLoop" not in self.bg_changes_effect:
                raise OptionWarning("bg_changes", "BGChanges beat is present but BGChanges stretchnoloop is not set to true. Video will loop at end if unspecified")
