"""This module provides functions for managing logs."""

import logging
import sys

logger = logging.getLogger('api')
logger.setLevel(logging.DEBUG)
logger.propagate = False

stream_handler = logging.StreamHandler(sys.stdout)
formatter = logging.Formatter(
    '%(asctime)s - %(levelname)s - %(message)s', '%Y-%m-%dT%H:%M:%S%z'
)

stream_handler.setFormatter(formatter)
logger.addHandler(stream_handler)
