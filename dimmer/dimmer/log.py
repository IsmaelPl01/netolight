import logging
import sys


logger = logging.getLogger('dimmer')
logger.setLevel(logging.DEBUG)
logger.addHandler(logging.StreamHandler(sys.stdout))
