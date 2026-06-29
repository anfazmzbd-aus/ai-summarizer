import logging
from pathlib import Path

Path("logs").mkdir(
    exist_ok=True
)


logging.basicConfig(
    level=logging.INFO,
    format=(
        "%(asctime)s | "
        "%(levelname)s | "
        "%(message)s"
    ),
    handlers=[
        logging.FileHandler(
            "logs/agent_system.log"
        ),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(
    "agent_system"
)
