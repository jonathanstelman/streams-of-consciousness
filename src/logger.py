import logging
import logging.config
import json
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
CACHE_DIR = PROJECT_ROOT / "config"
CONFIG_FILE = CACHE_DIR / "logging_config.json"

def setup_logging(config_file=CONFIG_FILE):
    """Creates a new instance of the logger configuration"""
    with open(config_file, "r", encoding="utf-8") as f:
        config = json.load(f)
    logging.config.dictConfig(config)

# Initialize the logger
setup_logging()
logger = logging.getLogger(__name__)
