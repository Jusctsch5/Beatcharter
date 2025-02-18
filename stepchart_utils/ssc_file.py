"""
SSCFile is a class that represents an SSC file.
It is a subclass of SMFile, and adds options such as jacket.
"""

from __future__ import annotations
from dataclasses import dataclass, field
import logging
from pathlib import Path
from typing import List

from stepchart_utils.common_parser import (
    FileMissing,
    FileUnspecified,
    OptionWarning,
    extract_value,
    find_audio_file,
    find_video_file,
)
from stepchart_utils.sm_file import SMFile

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


@dataclass
class SSCFile:
    filepath: Path = (
        None  # todo remove this and combine in Chart object, technically not SM
    )
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
    cd_title: str = ""
    music: str = ""
    offset: float = 0.0
    sample_start: float = 0.0
    sample_length: float = 0.0
    selectable: str = "YES"
    list_sort: str = ""
    bpms: list[tuple[float, float]] = field(default_factory=list)
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
    unknown_options: dict[str, str] = field(default_factory=dict)
    jacket: str = ""

    def __post_init__(self):
        if self.notes is None:
            self.notes = []

    def parse(self, filepath: Path) -> tuple[SSCFile, Path, Path]:
        """Parse an SSC file and return an SSCFile object"""

        ssc_file = SSCFile()

        with open(filepath, "r", encoding="utf-8") as f:
            content = f.read()

        # Parse basic metadata
        ssc_file.filepath = filepath
        ssc_file.title = extract_value(content, "TITLE")
        ssc_file.subtitle = extract_value(content, "SUBTITLE")
        ssc_file.artist = extract_value(content, "ARTIST")
        ssc_file.genre = extract_value(content, "GENRE")
        ssc_file.credit = extract_value(content, "CREDIT")
        ssc_file.menu_color = extract_value(content, "MENUCOLOR")
        ssc_file.meter_type = extract_value(content, "METERTYPE")
        ssc_file.banner = extract_value(content, "BANNER")
        ssc_file.background = extract_value(content, "BACKGROUND")
        ssc_file.lyrics_path = extract_value(content, "LYRICSPATH")
        ssc_file.cd_title = extract_value(content, "CDTITLE")
        ssc_file.music = extract_value(content, "MUSIC")
        ssc_file.jacket = extract_value(content, "JACKET")

        # Parse numeric values
        offset = extract_value(content, "OFFSET")
        ssc_file.offset = float(offset) if offset else 0.0

        sample_start = extract_value(content, "SAMPLESTART")
        ssc_file.sample_start = float(sample_start) if sample_start else 0.0

        sample_length = extract_value(content, "SAMPLELENGTH")
        ssc_file.sample_length = float(sample_length) if sample_length else 0.0

        # Parse other metadata
        ssc_file.selectable = extract_value(content, "SELECTABLE")
        ssc_file.list_sort = extract_value(content, "LISTSORT")

        bpms = extract_value(content, "BPMS")
        if bpms:
            ssc_file.bpms = [
                (float(bpm[0]), float(bpm[1]))
                for bpm in [bpm.split("=") for bpm in bpms.split(",")]
            ]
        else:
            ssc_file.bpms = []

        ssc_file.stops = extract_value(content, "STOPS")
        bg_changes = extract_value(content, "BGCHANGES")
        ssc_file.bg_changes = ssc_file._parse_bgchange(bg_changes)

        ssc_file.attacks = extract_value(content, "ATTACKS")

        # TODO: Implement notes parsing

        if ssc_file.bg_changes_file:
            video_file = ssc_file.filepath.parent / ssc_file.bg_changes_file
        else:
            video_file = find_video_file(ssc_file.filepath.parent)
        if ssc_file.music:
            audio_file = ssc_file.filepath.parent / ssc_file.music
        else:
            audio_file = find_audio_file(ssc_file.filepath.parent)

        for line in content.split("\n"):
            if line.startswith("#"):
                option = line[1:].split(":")[0]
                if option not in ssc_file.get_valid_options():
                    ssc_file.unknown_options[option] = (
                        line  # Technically should be every line until the next #FOO, but this is good enough to warn on.
                    )

        return ssc_file, audio_file, video_file

    def validate(self):
        chart_dir = self.filepath.parent
        logger.debug(f"Validate SSC file: {chart_dir}")

        # We want to have a jacket, banner, and background
        if not self.jacket:
            raise FileUnspecified("jacket")
        if self.jacket and not (chart_dir / self.jacket).exists():
            raise FileMissing(f"Jacket file {self.jacket} does not exist")

        if self.filepath is None:
            raise ValueError("Filepath is required")
        if not self.filepath.exists():
            raise FileMissing(f"File {self.filepath} does not exist")

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
            logger.debug(f"Offset: {self.offset}")
            logger.debug(f"BPMs: {self.bpms}")
            bpm = self.bpms[0][1]
            calculated_bg_changes_beat = self.offset * bpm / 60
            calculated_bg_changes_beat = round(calculated_bg_changes_beat, 3)
            logger.debug(f"Calculated BGChanges beat: ~{calculated_bg_changes_beat}")

            # Check if the BGChanges beat is 0
            if self.bg_changes_beat == 0:
                raise OptionWarning(
                    "bg_changes",
                    f"Offset is not zero ({self.offset}) but BGChanges beat is 0. Likely may see offset in audio/video. Calculated BGChanges beat: {calculated_bg_changes_beat}",
                )

            # If the BGChanges beat is specified, but is off by >= 1.0, then we should warn
            if self.bg_changes_beat != calculated_bg_changes_beat:
                offset_diff = abs(self.bg_changes_beat - calculated_bg_changes_beat)
                if offset_diff >= 1.0:
                    raise OptionWarning(
                        "bg_changes",
                        f"Offset is not zero ({self.offset}) but BGChanges beat is not equal to calculated BGChanges beat. Likely may see offset in audio/video. Calculated BGChanges beat: {calculated_bg_changes_beat}. Offset difference: {offset_diff}",
                    )

        if self.bg_changes_beat != 0:
            if self.bg_changes_file == "":
                raise OptionWarning(
                    "bg_changes",
                    "BGChanges beat is present but BGChanges file is not specified",
                )

            if (
                self.bg_changes_stretchnoloop is False
                and "StretchNoLoop" not in self.bg_changes_effect
            ):
                raise OptionWarning(
                    "bg_changes",
                    "BGChanges beat is present but BGChanges stretchnoloop is not set to true. Video will loop at end if unspecified",
                )

        if self.unknown_options:
            raise OptionWarning("sm_file", f"Unknown options: {self.unknown_options}")

    def _parse_bgchange(self, bgchange_line: str):
        # Default values
        defaults = {
            "beat": 0,
            "file": "",
            "update_rate": 1,
            "crossfade": False,
            "stretchrewind": False,
            "stretchnoloop": True,
            "effect": None,
            "file2": None,
            "transition": None,
            "color1": None,
            "color2": None,
        }

        # Remove #BGCHANGES: prefix and trailing semicolon
        if bgchange_line.startswith("#BGCHANGES:"):
            bgchange_line = bgchange_line[11:]
        if bgchange_line.endswith(";"):
            bgchange_line = bgchange_line[:-1]

        # Split the line by '='
        parts = bgchange_line.split("=")

        # Create result dictionary starting with defaults
        result = defaults.copy()

        # Update values based on the parts we have
        if len(parts) > 0 and parts[0]:
            self.bg_changes_beat = float(parts[0])
        if len(parts) > 1 and parts[1]:
            self.bg_changes_file = parts[1]
        if len(parts) > 2 and parts[2]:
            self.bg_changes_update_rate = float(parts[2])
        if len(parts) > 3 and parts[3]:
            self.bg_changes_crossfade = parts[3] == "1"
        if len(parts) > 4 and parts[4]:
            self.bg_changes_stretchrewind = parts[4] == "1"
        if len(parts) > 5 and parts[5]:
            self.bg_changes_stretchnoloop = parts[5] == "1"
        if len(parts) > 6 and parts[6]:
            self.bg_changes_effect = parts[6]
        if len(parts) > 7 and parts[7]:
            self.bg_changes_file2 = parts[7]
        if len(parts) > 8 and parts[8]:
            self.bg_changes_transition = parts[8]
        if len(parts) > 9 and parts[9]:
            self.bg_changes_color1 = parts[9]
        if len(parts) > 10 and parts[10]:
            self.bg_changes_color2 = parts[10]

        return result

    @classmethod
    def get_valid_options(cls):
        opts = [
            "TITLE",
            "SUBTITLE",
            "ARTIST",
            "TITLETRANSLIT",
            "SUBTITLETRANSLIT",
            "ARTISTTRANSLIT",
            "GENRE",
            "CREDIT",
            "MUSIC",
            "BANNER",
            "BACKGROUND",
            "CDTITLE",
            "JACKET",
            "SAMPLESTART",
            "SAMPLELENGTH",
            "SELECTABLE",
            "OFFSET",
            "BPMS",
            "STOPS",
            "MENUCOLOR",
            "METERTYPE",
            "LISTSORT",
            "BGCHANGES",
            "FGCHANGES",
            "NOTEDATA",
            "STEPSTYPE",
            "DESCRIPTION",
            "DIFFICULTY",
            "METER",
            "NOTES",
        ]
        return opts
