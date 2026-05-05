import os
import sys
import logging
from logging.handlers import RotatingFileHandler
from pathlib import Path
from pythonjsonlogger.json import JsonFormatter

def setup_logging(log_file="output/scraper.log"):
    # Convert log_file to an absolute path based on the script's location
    base_dir = Path(__file__).parent
    log_path = base_dir / log_file
    
    # Ensure the parent directory exists
    log_path.parent.mkdir(parents=True, exist_ok=True)
    
    # Determine base log level
    log_level_str = os.getenv("LOG_LEVEL", "INFO").upper()
    log_level = logging.getLevelName(log_level_str)
    
    # Format para local rotativo (Plain Text)
    file_formatter = logging.Formatter(
        fmt="%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
        datefmt="%Y-%m-%dT%H:%M:%S%z"
    )

    # JSON formatter para stdout (k8s -> Promtail -> Loki)
    json_formatter = JsonFormatter(
        "%(asctime)s %(levelname)s %(name)s %(message)s",
        rename_fields={"asctime": "timestamp", "levelname": "level", "name": "logger"},
        timestamp=True,
    )
    
    # File Handler
    file_handler = RotatingFileHandler(
        filename=str(log_path),
        maxBytes=2_000_000,
        backupCount=3,
        encoding="utf-8"
    )
    file_handler.setFormatter(file_formatter)
    file_handler.setLevel(log_level)
    
    # Stream Handler (stdout)
    stream_handler = logging.StreamHandler(sys.stdout)
    stream_handler.setFormatter(json_formatter)
    stream_handler.setLevel(log_level)
    
    # Root logger setup
    root_logger = logging.getLogger()
    root_logger.setLevel(log_level)
    
    # Clear any existing handlers to prevent duplicates if called multiple times
    if root_logger.hasHandlers():
        root_logger.handlers.clear()
        
    root_logger.addHandler(file_handler)
    root_logger.addHandler(stream_handler)
