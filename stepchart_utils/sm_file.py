"""
SMFile is a class that represents an SM file.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import List
from pathlib import Path
import logging

from stepchart_utils.common_parser import (
    FileMissing,
    FileUnspecified,
    OptionWarning,
    extract_value,
    find_audio_file,
    find_video_file,
)
from stepchart_utils.step_chart_file import StepChartFile

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


@dataclass
class SMFile(StepChartFile):
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

    def __post_init__(self):
        if self.notes is None:
            self.notes = []

    @staticmethod
    def parse(filepath: Path) -> tuple[SMFile, Path, Path]:
        """Parse an SM file and return an SMFile object"""
        sm_file = SMFile()

        with open(filepath, "r", encoding="utf-8") as f:
            content = f.read()

        # Parse basic metadata
        sm_file.filepath = filepath
        sm_file.title = extract_value(content, "TITLE")
        sm_file.subtitle = extract_value(content, "SUBTITLE")
        sm_file.artist = extract_value(content, "ARTIST")
        sm_file.genre = extract_value(content, "GENRE")
        sm_file.credit = extract_value(content, "CREDIT")
        sm_file.menu_color = extract_value(content, "MENUCOLOR")
        sm_file.meter_type = extract_value(content, "METERTYPE")
        sm_file.banner = extract_value(content, "BANNER")
        sm_file.background = extract_value(content, "BACKGROUND")
        sm_file.lyrics_path = extract_value(content, "LYRICSPATH")
        sm_file.cd_title = extract_value(content, "CDTITLE")
        sm_file.music = extract_value(content, "MUSIC")

        # Parse numeric values
        offset = extract_value(content, "OFFSET")
        sm_file.offset = float(offset) if offset else 0.0

        sample_start = extract_value(content, "SAMPLESTART")
        sm_file.sample_start = float(sample_start) if sample_start else 0.0

        sample_length = extract_value(content, "SAMPLELENGTH")
        sm_file.sample_length = float(sample_length) if sample_length else 0.0

        # Parse other metadata
        sm_file.selectable = extract_value(content, "SELECTABLE")
        sm_file.list_sort = extract_value(content, "LISTSORT")

        # Convert BPMS to list of tuples
        # Example #BPMS:0.000=160.002,10.000=180.002;
        # Would be converted to [(0.0, 160.002), (10.0, 180.002)]
        bpms = extract_value(content, "BPMS")
        if bpms:
            sm_file.bpms = [
                (float(bpm[0]), float(bpm[1]))
                for bpm in [bpm.split("=") for bpm in bpms.split(",")]
            ]
        else:
            sm_file.bpms = []

        sm_file.stops = extract_value(content, "STOPS")
        bg_changes = extract_value(content, "BGCHANGES")
        sm_file.bg_changes = sm_file._parse_bgchange(bg_changes)

        sm_file.attacks = extract_value(content, "ATTACKS")

        # TODO: Implement notes parsing

        if sm_file.bg_changes_file:
            video_file = sm_file.filepath.parent / sm_file.bg_changes_file
        else:
            video_file = find_video_file(sm_file.filepath.parent)
        if sm_file.music:
            audio_file = sm_file.filepath.parent / sm_file.music
        else:
            audio_file = find_audio_file(sm_file.filepath.parent)

        # Now check for unknown options. Operate on the whole content string, look at each option #FOO and see if it's in the list of valid options. If it's not, add it to the unknown_options dict.
        for line in content.split("\n"):
            if line.startswith("#"):
                option = line[1:].split(":")[0]
                if option not in sm_file.get_valid_options():
                    sm_file.unknown_options[option] = (
                        line  # Technically should be every line until the next #FOO, but this is good enough to warn on.
                    )

        return sm_file, audio_file, video_file

    def validate(self):
        chart_dir = self.filepath.parent
        logger.debug(f"Validate SM file: {chart_dir}")

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
        """
        Parse a BGCHANGES line into its component parts with default values.

        BGCHANGE format:
        beat=file_or_folder=update_rate=crossfade=stretchrewind=stretchnoloop=Effect=File2=Transition=Color1=Color2;

        beat: The beat this BGCHANGE occurs on. Can be negative to start before the first beat.
        file_or_folder: The relative path to the file to use for the BGCHANGE. Lua files are allowed. If a folder is given, it looks for "default.lua".
        update_rate: The update rate of the BGCHANGE.
        crossfade: set to 1 if using a crossfade. Overriden by Effect.
        stretchrewind: set to 1 if using stretchrewind. Overriden by Effect.
        stretchnoloop: set to 1 if using stretchnoloop. Overriden by Effect.
        Effect: What BackgroundEffect to use.
        File2: The second file to load for this BGCHANGE.
        Transition: How the background transitions to this.
        Color1/Color2: Formatted as red^green^blue^alpha, with the values being from 1 to 0, Passed to the BackgroundEffect with the LuaThreadVaraible "Color1"/"Color2" in web hexadecimal format as a string. Alpha is optional.

        Examples:
                Beat   =File                  =UpdateRate   =CrossFade =StretchRewind =StretchNoLoop   =Effect        =File2 =Transition =Color1 =Color2
                -0.506 =sengoku3.mp4          =1.000        =1         =0             =0               =StretchNoLoop =      =CrossFade  =       =


            This chart has two oddities:
            1) specifies both CrossFade with a 1 with the explicit CrossFade argument as well as specifying a CrossFade transition.
            2) specifies 0 for the explicit StretchNoLoop argument, but yet specifies a StretchNoLoop effect.

            Would be more simply defined as the following:
                Beat   =File                  =UpdateRate   =CrossFade =StretchRewind =StretchNoLoop   =Effect        =File2 =Transition =Color1 =Color2
                -0.506 =sengoku3.mp4          =1.000        =1         =0             =1               =              =      =           =       =

                Or, without whitespace:
                -0.506=sengoku3.mp4=1.000=1=0=1=====

        """
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
            "NOTES",
        ]

        return opts
