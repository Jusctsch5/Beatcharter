import re
from pathlib import Path
import logging  

from .sm_file import SMFile

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


class Chart:
    def __init__(self, sm_file: SMFile, video_file: Path, audio_file: Path):
        self.sm_file = sm_file
        self.video_file = video_file
        self.audio_file = audio_file

    def validate(self):
        self.sm_file.validate()
        if self.video_file and not self.video_file.exists():
            raise FileNotFoundError(f"Video file {self.video_file} does not exist")
        if self.audio_file and not self.audio_file.exists():
            raise FileNotFoundError(f"Audio file {self.audio_file} does not exist")


class ChartParser:
    def __init__(self):
        pass
    
    def parse_bgchange(self, sm_file: SMFile, bgchange_line: str):
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
            'beat': 0,
            'file': "",
            'update_rate': 1,
            'crossfade': False,
            'stretchrewind': False,
            'stretchnoloop': True,
            'effect': None,
            'file2': None,
            'transition': None,
            'color1': None,
            'color2': None
        }
        
        # Remove #BGCHANGES: prefix and trailing semicolon
        if bgchange_line.startswith('#BGCHANGES:'):
            bgchange_line = bgchange_line[11:]
        if bgchange_line.endswith(';'):
            bgchange_line = bgchange_line[:-1]
        
        # Split the line by '='
        parts = bgchange_line.split('=')
        
        # Create result dictionary starting with defaults
        result = defaults.copy()
        
        # Update values based on the parts we have
        if len(parts) > 0 and parts[0]:
            sm_file.bg_changes_beat = float(parts[0])
        if len(parts) > 1 and parts[1]:
            sm_file.bg_changes_file = parts[1]
        if len(parts) > 2 and parts[2]:
            sm_file.bg_changes_update_rate = float(parts[2])
        if len(parts) > 3 and parts[3]:
            sm_file.bg_changes_crossfade = parts[3] == '1'
        if len(parts) > 4 and parts[4]:
            sm_file.bg_changes_stretchrewind = parts[4] == '1'
        if len(parts) > 5 and parts[5]:
            sm_file.bg_changes_stretchnoloop = parts[5] == '1'
        if len(parts) > 6 and parts[6]:
            sm_file.bg_changes_effect = parts[6]
        if len(parts) > 7 and parts[7]:
            sm_file.bg_changes_file2 = parts[7]
        if len(parts) > 8 and parts[8]:
            sm_file.bg_changes_transition = parts[8]
        if len(parts) > 9 and parts[9]:
            sm_file.bg_changes_color1 = parts[9]
        if len(parts) > 10 and parts[10]:
            sm_file.bg_changes_color2 = parts[10]
        
        return result
    
    def parse_sm_file(self, filepath: Path) -> Chart:
        """Parse an SM file and return an SMFile object"""
        sm_file = SMFile()

        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()            

        # Parse basic metadata
        sm_file.filepath = filepath
        sm_file.title = self._extract_value(content, "TITLE")
        sm_file.subtitle = self._extract_value(content, "SUBTITLE")
        sm_file.artist = self._extract_value(content, "ARTIST")
        sm_file.genre = self._extract_value(content, "GENRE")
        sm_file.credit = self._extract_value(content, "CREDIT")
        sm_file.menu_color = self._extract_value(content, "MENUCOLOR")
        sm_file.meter_type = self._extract_value(content, "METERTYPE")
        sm_file.banner = self._extract_value(content, "BANNER")
        sm_file.background = self._extract_value(content, "BACKGROUND")
        sm_file.lyrics_path = self._extract_value(content, "LYRICSPATH")
        sm_file.cd_title = self._extract_value(content, "CDTITLE")
        sm_file.music = self._extract_value(content, "MUSIC")
        sm_file.jacket = self._extract_value(content, "JACKET")
        
        # Parse numeric values
        offset = self._extract_value(content, "OFFSET")
        sm_file.offset = float(offset) if offset else 0.0
        
        sample_start = self._extract_value(content, "SAMPLESTART")
        sm_file.sample_start = float(sample_start) if sample_start else 0.0
        
        sample_length = self._extract_value(content, "SAMPLELENGTH")
        sm_file.sample_length = float(sample_length) if sample_length else 0.0
        
        # Parse other metadata
        sm_file.selectable = self._extract_value(content, "SELECTABLE")
        sm_file.list_sort = self._extract_value(content, "LISTSORT")

        # Convert BPMS to list of tuples
        # Example #BPMS:0.000=160.002,10.000=180.002;
        # Would be converted to [(0.0, 160.002), (10.0, 180.002)]
        bpms = self._extract_value(content, "BPMS")
        if bpms:
            sm_file.bpms = [(float(bpm[0]), float(bpm[1])) for bpm in [bpm.split('=') for bpm in bpms.split(',')]]
        else:
            sm_file.bpms = []

        sm_file.stops = self._extract_value(content, "STOPS")
        bg_changes = self._extract_value(content, "BGCHANGES")
        sm_file.bg_changes = self.parse_bgchange(sm_file, bg_changes)

        sm_file.attacks = self._extract_value(content, "ATTACKS")

        # TODO: Implement notes parsing

        if sm_file.bg_changes_file:
            video_file = sm_file.filepath.parent / sm_file.bg_changes_file
        else:
            sm_dir = sm_file.filepath.parent
            video_files = list(sm_dir.glob('*.avi')) + list(sm_dir.glob('*.mp4'))
            if video_files:
                # video_file is a Path object
                video_file = video_files[0]
        if sm_file.music:
            audio_file = sm_file.filepath.parent / sm_file.music
        else:
            sm_dir = sm_file.filepath.parent
            audio_files = list(sm_dir.glob('*.mp3')) + list(sm_dir.glob('*.ogg')) + list(sm_dir.glob('*.wav'))
            if audio_files:
                audio_file = audio_files[0]

        chart = Chart(sm_file, video_file, audio_file)
        return chart
    
    def _extract_value(self, content: str, key: str) -> str:
        """Extract value from SM file format #KEY:value;"""
        pattern = f"#{key}:([^;]*?);"
        match = re.search(pattern, content, re.DOTALL)
        return match.group(1).strip() if match else ""
    
