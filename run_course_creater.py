import argparse
import logging
from pathlib import Path

from stepchart_utils.chart_parser import ChartParser
from concreator.course_creator import generate_courses_for_directory

logging.basicConfig(level=logging.INFO, format="%(filename)s:%(lineno)d - %(message)s")
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


def main():
    parser = argparse.ArgumentParser(
        description="Generate StepMania course files for each subsong directory"
    )
    parser.add_argument(
        "--songs-dir",
        type=str,
        default="/home/john/Stepmania/Songs",
        help="Path to the Songs directory (default: /home/john/Stepmania/Songs)",
    )
    parser.add_argument(
        "--courses-dir",
        type=str,
        default="/home/john/Stepmania/Courses",
        help="Path to the Courses directory (default: /home/john/Stepmania/Courses)",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        default=False,
        help="Show what would be generated without creating files",
    )
    args = parser.parse_args()

    songs_dir = Path(args.songs_dir)
    courses_dir = Path(args.courses_dir)
    chart_parser = ChartParser()

    generate_courses_for_directory(
        songs_dir=songs_dir,
        courses_dir=courses_dir,
        chart_parser=chart_parser,
        dry_run=args.dry_run,
    )


if __name__ == "__main__":
    main()
