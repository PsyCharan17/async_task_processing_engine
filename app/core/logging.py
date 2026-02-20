import logging
import sys

logging.basicConfig(
    level="INFO",
    format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)]
)

logger = logging.getLogger("async-task-engine")