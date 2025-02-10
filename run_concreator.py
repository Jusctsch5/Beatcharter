import argparse
import logging
from pathlib import Path
from concreator.concreator import create_dynamic_assets
from stepchart_utils.chart_parser import Chart, ChartParser

logging.basicConfig(format='%(filename)s:%(lineno)d - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)

def process_sm_file(sm_file: Path, output_dir: Path) -> None:
    """Process a single SM file and create its dynamic assets"""
    try:
        sm_parser = ChartParser()
        parsed_chart: Chart = sm_parser.parse_sm_file(sm_file)
        
        # Create output directory based on song directory name
        logger.info(f"Processing: {sm_file.relative_to(sm_file.parent.parent)}")
        
        create_dynamic_assets(parsed_chart, output_dir)
        logger.info(f"Successfully created assets for: {sm_file.parent.name}")
    except Exception as e:
        logger.exception(f"Error processing {sm_file}: {str(e)}")

def find_sm_files(directory: Path) -> list[Path]:
    """Recursively find all .sm files in the given directory"""
    return list(directory.rglob("*.sm"))

def main():
    parser = argparse.ArgumentParser(description='Create dynamic assets from SM files')
    parser.add_argument('path', type=str, help='Path to SM file or directory containing SM files')
    parser.add_argument('--output', '-o', type=str, default='output', 
                       help='Output directory for dynamic assets (default: output)')
    args = parser.parse_args()
    
    path = Path(args.path)
    output_dir = Path(args.output)
    
    if not path.exists():
        logger.error(f"Error: Path {path} does not exist")
        return

    # Create output directory
    output_dir.mkdir(parents=True, exist_ok=True)

    # Handle single file
    if path.is_file():
        if path.suffix.lower() != '.sm':
            logger.error(f"Error: {path} is not an SM file")
            return
        process_sm_file(path, output_dir)
    
    # Handle directory
    else:
        sm_files = find_sm_files(path)
        logger.info(f"Found {len(sm_files)} SM files to process")
        
        for sm_file in sm_files:
            process_sm_file(sm_file, output_dir)
        
        logger.info("Finished processing all files")

if __name__ == "__main__":
    main()
    