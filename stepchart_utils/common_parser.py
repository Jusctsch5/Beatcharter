from pathlib import Path
import re


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


def extract_value(content: str, key: str) -> str:
    """Extract value from SM file format #KEY:value;"""
    pattern = f"#{key}:([^;]*?);"
    match = re.search(pattern, content, re.DOTALL)
    return match.group(1).strip() if match else ""


def find_video_file(chart_dir: Path) -> Path:
    video_files = list(chart_dir.glob("*.avi")) + list(chart_dir.glob("*.mp4"))
    if video_files:
        return video_files[0]
    return None


def find_audio_file(chart_dir: Path) -> Path:
    audio_files = (
        list(chart_dir.glob("*.flac"))
        + list(chart_dir.glob("*.mp3"))
        + list(chart_dir.glob("*.ogg"))
        + list(chart_dir.glob("*.wav"))
    )
    if audio_files:
        return audio_files[0]
    return None
