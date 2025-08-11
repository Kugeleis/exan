import shutil
from pathlib import Path
import logging

logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")

def clean_output_directory():
    """
    Removes all files and subdirectories within the 'output' directory
    without deleting the directory itself.
    """
    output_dir = Path("output")
    if not output_dir.is_dir():
        logging.info(f"Output directory '{output_dir}' not found or is not a directory. Nothing to clean.")
        return

    logging.info(f"Cleaning contents of '{output_dir}' directory...")
    for item in output_dir.iterdir():
        try:
            if item.is_dir():
                shutil.rmtree(item)
                logging.info(f"Removed directory: {item}")
            else:
                item.unlink()
                logging.info(f"Removed file: {item}")
        except Exception as e:
            logging.error(f"Error removing {item}: {e}")
    logging.info("Cleaning complete.")

if __name__ == "__main__":
    clean_output_directory()
