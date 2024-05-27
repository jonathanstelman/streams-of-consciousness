import json
import os
from pathlib import Path

from logger import logger


PROJECT_ROOT = Path(__file__).resolve().parent.parent
CACHE_DIR = PROJECT_ROOT / "cache"
CACHE_FILE = CACHE_DIR / "cpi_cache.json"

def load_cache():
    """Reads the cache file from disk"""
    if os.path.exists(CACHE_FILE):
        with open(CACHE_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    else:
        return {}

def save_cache(cache_data):
    """Saves a new cache file to disk"""
    with open(CACHE_FILE, "w", encoding="utf-8") as f:
        json.dump(cache_data, f)

def disk_cache(func):
    """Decorator to save and load function results to and from the disk"""
    cache = load_cache()

    def wrapper(*args, **kwargs):
        cache_key = f"{func.__name__}_{args}_{kwargs}"
        if cache_key in cache:
            logger.debug('Retrieved results from cache')
            return cache[cache_key]

        result = func(*args, **kwargs)
        cache[cache_key] = result
        logger.debug('Caching result to %s', cache_key)
        save_cache(cache)

        return result

    return wrapper
