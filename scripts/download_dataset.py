"""
Download Script for Madhav E-Commerce Sales Dataset.
Downloads Orders.csv and Details.csv into data/raw/ from legitimate public repository mirrors.
"""
import os
import sys
import urllib.request
import logging

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger(__name__)

# Base directory for the project
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RAW_DATA_DIR = os.path.join(BASE_DIR, "data", "raw")

# Public repositories containing the authentic Madhav E-Commerce Sales Dataset
DATASET_SOURCES = {
    "Orders.csv": [
        "https://raw.githubusercontent.com/Harshit-2806/Madhav-Ecommerce-Dashboard-using-PowerBI/main/Orders.csv",
        "https://raw.githubusercontent.com/Parashu96/Madhav_Store_PowerBI_Dashboard/main/Orders.csv",
    ],
    "Details.csv": [
        "https://raw.githubusercontent.com/Harshit-2806/Madhav-Ecommerce-Dashboard-using-PowerBI/main/Details.csv",
        "https://raw.githubusercontent.com/Parashu96/Madhav_Store_PowerBI_Dashboard/main/Details.csv",
    ]
}


def download_file(filename: str, urls: list, dest_dir: str) -> str:
    os.makedirs(dest_dir, exist_ok=True)
    target_path = os.path.join(dest_dir, filename)

    if os.path.exists(target_path) and os.path.getsize(target_path) > 100:
        logger.info(f"File already exists and is valid: {target_path} ({os.path.getsize(target_path)} bytes)")
        return target_path

    logger.info(f"Downloading {filename}...")
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"}

    last_error = None
    for url in urls:
        try:
            logger.info(f"Attempting source: {url}")
            req = urllib.request.Request(url, headers=headers)
            with urllib.request.urlopen(req, timeout=30) as response, open(target_path, "wb") as out_file:
                out_file.write(response.read())
            size = os.path.getsize(target_path)
            if size > 100:
                logger.info(f"Successfully downloaded {filename} ({size} bytes) to {target_path}")
                return target_path
            else:
                logger.warning(f"Downloaded file {filename} was too small ({size} bytes). Trying next source.")
        except Exception as e:
            logger.warning(f"Failed to download from {url}: {e}")
            last_error = e

    raise RuntimeError(f"Unable to download {filename} from any configured source. Last error: {last_error}")


def download_all():
    logger.info("Starting download of Madhav E-Commerce Sales Dataset...")
    results = {}
    for filename, urls in DATASET_SOURCES.items():
        results[filename] = download_file(filename, urls, RAW_DATA_DIR)
    logger.info("All raw dataset files successfully downloaded and verified.")
    return results


if __name__ == "__main__":
    try:
        download_all()
    except Exception as exc:
        logger.error(f"Download failed: {exc}")
        sys.exit(1)
