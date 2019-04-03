import os
import sys

USER_DIR = os.path.expanduser("~")
ROOT_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_PATH = os.path.join(ROOT_DIR, "data")
OUTPUT_PATH = os.path.join(USER_DIR, ".nuaal", "outputs")
LOG_PATH = os.path.join(USER_DIR, ".nuaal", "logs")
TIMESTAMP_FORMAT = "%Y-%m-%d %H:%M:%S"
