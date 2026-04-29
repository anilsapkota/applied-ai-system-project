import logging
import os
from datetime import datetime


def setup_logging(log_level: str = "INFO") -> logging.Logger:
    os.makedirs("logs", exist_ok=True)
    log_file = f"logs/vibematch_{datetime.now().strftime('%Y%m%d')}.log"

    logging.basicConfig(
        level=getattr(logging, log_level.upper(), logging.INFO),
        format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
        handlers=[
            logging.FileHandler(log_file, encoding="utf-8"),
            logging.StreamHandler(),
        ],
        force=True,
    )
    return logging.getLogger("vibematch")
