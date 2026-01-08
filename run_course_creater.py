import argparse
import logging
from pathlib import Path

from stepchart_utils.chart_parser import ChartParser
from concreator.course_creator import generate_courses_for_directory
from config_utils import load_config, get_config_value

logging.basicConfig(level=logging.INFO, format="%(filename)s:%(lineno)d - %(message)s")
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


def main():
    parser = argparse.ArgumentParser(
        description="Generate StepMania course files for each subsong directory"
    )
    parser.add_argument(
        "--config",
        type=str,
        default="beatcharter.toml",
        help="Path to TOML config file (default: beatcharter.toml)",
    )
    parser.add_argument(
        "--songs-dir",
        type=str,
        help="Path to the Songs directory (overrides config file)",
    )
    parser.add_argument(
        "--courses-dir",
        type=str,
        help="Path to the Courses directory (overrides config file)",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        default=False,
        help="Show what would be generated without creating files",
    )
    args = parser.parse_args()

    # Load config
    config = load_config(Path(args.config))
    
    # Get values from config or command line (CLI takes precedence)
    songs_dir = args.songs_dir if args.songs_dir else get_config_value(config, "course_creator", "songs_dir", None)
    courses_dir = args.courses_dir if args.courses_dir else get_config_value(config, "course_creator", "courses_dir", None)
    
    if not songs_dir:
        parser.error("songs_dir is required (either via --songs-dir or in config file [course_creator] section)")
    if not courses_dir:
        parser.error("courses_dir is required (either via --courses-dir or in config file [course_creator] section)")
    
    songs_dir = Path(songs_dir)
    courses_dir = Path(courses_dir)
    
    chart_parser = ChartParser()

    generate_courses_for_directory(
        songs_dir=songs_dir,
        courses_dir=courses_dir,
        chart_parser=chart_parser,
        dry_run=args.dry_run,
    )


if __name__ == "__main__":
    main()
