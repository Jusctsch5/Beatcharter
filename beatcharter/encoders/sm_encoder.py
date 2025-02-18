import os
import shutil
from pathlib import Path


class SMEncoder:
    HEADER = """#TITLE:$TITLE;
#SUBTITLE:;
#ARTIST:;
#TITLETRANSLIT:;
#SUBTITLETRANSLIT:;
#ARTISTTRANSLIT:;
#GENRE:;
#CREDIT:AutoStepper by phr00t.com;
#BANNER:$BGIMAGE;
#BACKGROUND:$BGIMAGE;
#LYRICSPATH:;
#CDTITLE:;
#MUSIC:$MUSICFILE;
#OFFSET:$STARTTIME;
#SAMPLESTART:30.0;
#SAMPLELENGTH:30.0;
#SELECTABLE:YES;
#BPMS:0.000000=$BPM;
#STOPS:;
#KEYSOUNDS:;
#ATTACKS:;"""

    BEGINNER = "Beginner:\n     2:"
    EASY = "Easy:\n     4:"
    MEDIUM = "Medium:\n     6:"
    HARD = "Hard:\n     8:"
    CHALLENGE = "Challenge:\n     10:"

    CHART_HEADER = """//---------------dance-single - ----------------
#NOTES:
     dance-single:
     :
     $DIFFICULTY
     0.733800,0.772920,0.048611,0.850698,0.060764,634.000000,628.000000,6.000000,105.000000,8.000000,0.000000,0.733800,0.772920,0.048611,0.850698,0.060764,634.000000,628.000000,6.000000,105.000000,8.000000,0.000000:
$NOTES
;

"""

    @staticmethod
    def add_notes(sm_file, difficulty: str, notes: str) -> None:
        """Add notes to the SM file for a specific difficulty."""
        try:
            sm_file.write(
                SMEncoder.CHART_HEADER.replace("$DIFFICULTY", difficulty).replace(
                    "$NOTES", notes
                )
            )
        except Exception:
            pass

    @staticmethod
    def complete(sm_file) -> None:
        """Close the SM file."""
        try:
            sm_file.close()
        except Exception:
            pass

    @staticmethod
    def get_sm_file(song_file: Path, output_dir: str) -> Path:
        """Get the path for the SM file."""
        filename = song_file.name
        directory = Path(output_dir) / f"{filename}_dir"
        return directory / f"{filename}.sm"

    @staticmethod
    def generate_sm(bpm: float, start_time: float, song_file: Path, output_dir: str):
        """
        Generate a new SM file.

        Args:
            bpm: Beats per minute of the song
            start_time: Start time of the song
            song_file: Path to the song file
            output_dir: Directory to output the SM file

        Returns:
            file object: The opened SM file writer
        """
        filename = song_file.name
        song_name = Path(filename).stem
        short_name = song_name[:32] if len(song_name) > 32 else song_name

        # Create directory
        directory = Path(output_dir) / filename
        directory.mkdir(parents=True, exist_ok=True)

        sm_file = directory / f"{filename}.sm"

        try:
            # Remove old file if it exists
            if sm_file.exists():
                sm_file.unlink()

            # Copy song file to new directory
            shutil.copy2(song_file, directory / filename)

            # Create and write to new SM file
            with open(sm_file, "w") as writer:
                header_content = (
                    SMEncoder.HEADER.replace("$TITLE", short_name)
                    .replace("$MUSICFILE", filename)
                    .replace("$STARTTIME", str(start_time))
                    .replace("$BPM", str(bpm))
                )
                writer.write(header_content)
                return writer

        except Exception:
            return None
