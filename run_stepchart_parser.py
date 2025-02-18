import argparse
import logging
from pathlib import Path
from typing import List
from stepchart_utils.chart_parser import Chart, ChartParser
from stepchart_utils.common_parser import ParseError

logging.basicConfig(level=logging.INFO, format="%(filename)s:%(lineno)d - %(message)s")
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

chart_parser = ChartParser()


def parse_chart_file(chart_file_path: Path) -> Chart:
    """Process a single SM file and return the parsed result"""
    try:
        result: Chart = chart_parser.parse_file(chart_file_path)
        result.validate()
        logger.debug(
            f"Successfully parsed: {chart_file_path.relative_to(chart_file_path.parent.parent)}"
        )
        return result
    except ParseError as e:
        logger.error(f"Error processing {chart_file_path}: {str(e)}")
        return None
    except Exception as e:
        logger.exception(f"Unexpected error processing {chart_file_path}: {str(e)}")
        return None


def find_sm_files(directory: Path) -> list[Path]:
    """Recursively find all .sm files in the given directory"""
    return list(directory.rglob("*.sm"))


def main():
    parser = argparse.ArgumentParser(description="Parse Stepmania SM files")
    parser.add_argument(
        "path", type=str, help="Path to SM file or directory containing SM files"
    )
    parser.add_argument(
        "--output", "-o", type=str, help="Output file for parsed data (optional)"
    )
    args = parser.parse_args()

    path = Path(args.path)
    if not path.exists():
        logger.error(f"Error: Path {path} does not exist")
        return

    results: List[Chart] = []
    # Handle single file
    if path.is_file():
        if not chart_parser.is_chart_file(path):
            logger.error(f"Error: {path} is not a chart file")
            return
        results = []
        result = parse_chart_file(path)
        if result:
            results.append(result)

    # Handle directory
    else:
        chart_files = chart_parser.get_chart_files_from_directory(path)
        logger.info(f"Found {len(chart_files)} Chart files to process")

        results = []
        errors = []
        for chart_file_path in chart_files:
            try:
                result = parse_chart_file(chart_file_path)
                if result:
                    results.append(result)
            except Exception as e:
                errors.append(f"Error processing {chart_file_path}: {str(e)}")

        if errors:
            logger.error("Errors encountered during processing:")
            for error in errors:
                logger.error(error)

        logger.info(f"Found {len(results)} of {len(chart_files)} valid Chart files")

    # Print results
    if logger.getEffectiveLevel() == logging.DEBUG:
        for result in results:
            print("\n-------------------")
            print(f"Chart: {result.chart_file_path.filepath}")
            for key, value in vars(result).items():
                if key != "filepath":  # Skip filepath since we already printed it
                    print(f"    {key}: {value}")


if __name__ == "__main__":
    main()
