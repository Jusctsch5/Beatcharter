import argparse
import logging
from pathlib import Path
from stepchart_utils.chart_parser import Chart, ChartParser
from stepchart_utils.sm_file import ParseError

logging.basicConfig(level=logging.INFO, format='%(filename)s:%(lineno)d - %(message)s')
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

def process_sm_file(sm_file: Path) -> Chart:
    """Process a single SM file and return the parsed result"""
    try:
        sm_parser = ChartParser()
        result: Chart = sm_parser.parse_sm_file(sm_file)
        result.validate()
        logger.debug(f"Successfully parsed: {sm_file.relative_to(sm_file.parent.parent)}")
        return result
    except ParseError as e:
        logger.error(f"Error processing {sm_file}: {str(e)}")
        return None
    except Exception as e:
        logger.exception(f"Error processing {sm_file}: {str(e)}")
        return None
    

def find_sm_files(directory: Path) -> list[Path]:
    """Recursively find all .sm files in the given directory"""
    return list(directory.rglob("*.sm"))

def main():
    parser = argparse.ArgumentParser(description='Parse Stepmania SM files')
    parser.add_argument('path', type=str, help='Path to SM file or directory containing SM files')
    parser.add_argument('--output', '-o', type=str, help='Output file for parsed data (optional)')
    args = parser.parse_args()
    
    path = Path(args.path)
    if not path.exists():
        logger.error(f"Error: Path {path} does not exist")
        return

    # Handle single file
    if path.is_file():
        if path.suffix.lower() != '.sm':
            logger.error(f"Error: {path} is not an SM file")
            return
        results = []
        result = process_sm_file(path)
        if result:
            results.append(result)
    
    # Handle directory
    else:
        sm_files = find_sm_files(path)
        logger.info(f"Found {len(sm_files)} SM files to process")

        results = []
        errors = []
        for sm_file in sm_files:
            try:
                result = process_sm_file(sm_file)
                if result:
                    results.append(result)
            except Exception as e:
                errors.append(f"Error processing {sm_file}: {str(e)}")
                
        if errors:
            logger.error("Errors encountered during processing:")
            for error in errors:
                logger.error(error)

        logger.info(f"Found {len(results)} of {len(sm_files)} valid SM files")

    # Print results
    if logger.getEffectiveLevel() == logging.DEBUG:
        for result in results:
            print("\n-------------------")
            print(f"Chart: {result.sm_file.filepath}")
            for key, value in vars(result).items():
                if key != 'filepath':  # Skip filepath since we already printed it
                    print(f"    {key}: {value}")    

                

if __name__ == "__main__":
    main()