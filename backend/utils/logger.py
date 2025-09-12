"""
Logging-Konfiguration für XTTS V2 Voice Cloning Studio
"""

import sys
from loguru import logger
from pathlib import Path

def setup_logger():
    """Logger für die Anwendung konfigurieren"""
    
    # Standard-Logger entfernen
    logger.remove()
    
    # Console-Logger mit Farben
    logger.add(
        sys.stdout,
        format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>",
        level="INFO",
        colorize=True
    )
    
    # File-Logger für Debugging
    log_dir = Path("logs")
    log_dir.mkdir(exist_ok=True)
    
    logger.add(
        log_dir / "xtts_backend.log",
        format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {name}:{function}:{line} - {message}",
        level="DEBUG",
        rotation="10 MB",
        retention="7 days",
        compression="zip"
    )
    
    # Error-Logger
    logger.add(
        log_dir / "errors.log",
        format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {name}:{function}:{line} - {message}",
        level="ERROR",
        rotation="5 MB",
        retention="30 days"
    )
    
    return logger

def get_logger(name: str = None):
    """Logger für spezifisches Modul abrufen"""
    if name:
        return logger.bind(name=name)
    return logger