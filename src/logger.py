import logging
import logging.config
import json

def setup_logging(config_file="../config/logging_config.json"):
    """Creates a new instance of the logger configuration"""
    with open(config_file, "r", encoding="utf-8") as f:
        config = json.load(f)
    logging.config.dictConfig(config)

# Initialize the logger
setup_logging()
logger = logging.getLogger(__name__)
