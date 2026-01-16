"""
Structured logging system for NEO Risk API.
Provides consistent log formatting with timestamps and context.
"""

import logging
import sys
from datetime import datetime
from pathlib import Path
from typing import Optional

# Create logs directory if it doesn't exist
LOGS_DIR = Path("logs")
LOGS_DIR.mkdir(exist_ok=True)


def setup_logger(
    name: str = "neo_risk_api",
    level: int = logging.INFO,
    log_file: Optional[str] = None
) -> logging.Logger:
    """
    Set up a logger with console and optional file handlers.
    
    Args:
        name: Logger name
        level: Logging level
        log_file: Optional log file path
        
    Returns:
        Configured logger instance
    """
    logger = logging.getLogger(name)
    logger.setLevel(level)
    
    # Prevent duplicate handlers
    if logger.handlers:
        return logger
    
    # Log format
    formatter = logging.Formatter(
        fmt="%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S"
    )
    
    # Console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(level)
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)
    
    # File handler (if specified)
    if log_file:
        file_path = LOGS_DIR / log_file
        file_handler = logging.FileHandler(file_path, encoding="utf-8")
        file_handler.setLevel(level)
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)
    
    return logger


# Default application logger
logger = setup_logger(
    name="neo_risk_api",
    log_file=f"neo_api_{datetime.now().strftime('%Y%m%d')}.log"
)


def log_prediction(
    distance_km: float,
    velocity_kms: float,
    diameter_m: float,
    trajectory_angle_deg: float,
    risk_level: str,
    impact_probability: float
) -> None:
    """
    Log a prediction event with all parameters.
    
    Args:
        distance_km: Distance from Earth in km
        velocity_kms: Velocity in km/s
        diameter_m: Diameter in meters
        trajectory_angle_deg: Trajectory angle in degrees
        risk_level: Predicted risk level
        impact_probability: Impact probability
    """
    logger.info(
        f"PREDICTION | "
        f"Distance: {distance_km:.2f}km | "
        f"Velocity: {velocity_kms:.2f}km/s | "
        f"Diameter: {diameter_m:.2f}m | "
        f"Angle: {trajectory_angle_deg:.2f}° | "
        f"Risk: {risk_level} | "
        f"Probability: {impact_probability:.3f}"
    )


def log_api_request(
    method: str,
    path: str,
    status_code: int,
    duration_ms: float
) -> None:
    """
    Log an API request.
    
    Args:
        method: HTTP method
        path: Request path
        status_code: Response status code
        duration_ms: Request duration in milliseconds
    """
    logger.info(
        f"REQUEST | {method} {path} | Status: {status_code} | Duration: {duration_ms:.2f}ms"
    )
