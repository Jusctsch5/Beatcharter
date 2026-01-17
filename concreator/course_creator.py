import logging
from pathlib import Path
from typing import List, Set

from stepchart_utils.chart_parser import ChartParser

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


def find_chart_files_in_directory(directory: Path, chart_parser: ChartParser) -> List[Path]:
    """Find all .sm and .ssc files in a directory (non-recursive)"""
    chart_files = []
    for item in directory.iterdir():
        if item.is_file() and chart_parser.is_chart_file(item):
            chart_files.append(item)
    return chart_files


def get_song_title_from_chart(chart_file: Path, chart_parser: ChartParser) -> str:
    """Extract the song title from a chart file"""
    try:
        chart = chart_parser.parse_file(chart_file)
        title = chart.chart_file.title
        if not title:
            # Fallback to directory name if title is empty
            title = chart_file.parent.name
        return title.strip()
    except Exception as e:
        logger.warning(f"Error parsing {chart_file}: {e}. Using directory name as fallback.")
        return chart_file.parent.name


def get_songs_from_subsong_dir(subsong_dir: Path, chart_parser: ChartParser) -> List[str]:
    """Get all song entries from a subsong directory using folder names directly"""
    songs = []
    seen_entries: Set[str] = set()
    
    # Iterate through all subdirectories (song directories)
    for item in subsong_dir.iterdir():
        if item.is_dir():
            # Look for chart files in this song directory
            chart_files = find_chart_files_in_directory(item, chart_parser)
            if chart_files:
                # Use the directory name directly, not the title from the SM file
                folder_name = item.name
                # Avoid duplicates
                if folder_name not in seen_entries:
                    songs.append(folder_name)
                    seen_entries.add(folder_name)
    
    return sorted(songs)  # Sort for consistent ordering


def generate_course_file(course_name: str, songs: List[str], output_path: Path, dry_run: bool = False) -> None:
    """Generate a course file with the given name and songs"""
    if dry_run:
        logger.info(f"[DRY RUN] Would generate course file: {output_path} with {len(songs)} songs")
        logger.info(f"[DRY RUN] Course content would be:")
        logger.info(f"[DRY RUN]   #COURSE:{course_name};")
        logger.info(f"[DRY RUN]   #SCRIPTER:Auto-Generated;")
        for song in songs:
            logger.info(f"[DRY RUN]   #SONG:{song}:Hard:nodifficult;")
        return
    
    output_path.parent.mkdir(parents=True, exist_ok=True)
    
    with open(output_path, "w", encoding="utf-8") as f:
        # Write course header
        f.write(f"#COURSE:{course_name};\n")
        f.write("#SCRIPTER:Auto-Generated;\n")
        
        # Write each song entry
        for song in songs:
            f.write(f"#SONG:{song}:Hard:nodifficult;\n")
    
    logger.info(f"Generated course file: {output_path} with {len(songs)} songs")


def generate_courses_for_directory(
    songs_dir: Path,
    courses_dir: Path,
    chart_parser: ChartParser,
    dry_run: bool = False,
) -> None:
    """
    Generate course files for each subsong directory in the songs directory.
    
    Args:
        songs_dir: Path to the Songs directory containing subsong directories
        courses_dir: Path to the Courses directory where Generated folder will be created
        chart_parser: ChartParser instance to use for parsing chart files
        dry_run: If True, show what would be generated without creating files
    """
    if not songs_dir.exists():
        logger.error(f"Error: Songs directory {songs_dir} does not exist")
        return

    if not songs_dir.is_dir():
        logger.error(f"Error: {songs_dir} is not a directory")
        return

    # Create the Generated directory (skip in dry-run mode)
    generated_dir = courses_dir / "Generated"
    if not dry_run:
        generated_dir.mkdir(parents=True, exist_ok=True)
    else:
        logger.info("[DRY RUN] Would create directory: " + str(generated_dir))

    # Find all subsong directories (direct subdirectories of songs_dir)
    subsong_dirs = [d for d in songs_dir.iterdir() if d.is_dir()]

    if not subsong_dirs:
        logger.warning(f"No subsong directories found in {songs_dir}")
        return

    if dry_run:
        logger.info("[DRY RUN] Mode enabled - no files will be created")
    
    logger.info(f"Found {len(subsong_dirs)} subsong directories")

    # Process each subsong directory
    for subsong_dir in subsong_dirs:
        logger.info(f"Processing subsong directory: {subsong_dir.name}")
        songs = get_songs_from_subsong_dir(subsong_dir, chart_parser)

        if not songs:
            logger.warning(f"No songs found in {subsong_dir.name}, skipping")
            continue

        # Generate course file name: {subsong_dir_name}_All.crs
        # Course title keeps spaces, but filename replaces whitespace with underscores
        course_name = f"{subsong_dir.name} All"
        course_filename = course_name.replace(" ", "_")
        course_file_path = generated_dir / f"{course_filename}.crs"

        generate_course_file(course_name, songs, course_file_path, dry_run=dry_run)
        if not dry_run:
            logger.info(f"Generated course for {subsong_dir.name} with {len(songs)} songs")

    if dry_run:
        logger.info(f"[DRY RUN] Course generation preview complete! Would generate courses in {generated_dir}")
    else:
        logger.info(f"Course generation complete! Generated courses are in {generated_dir}")
