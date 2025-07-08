# Suppress deprecation warnings at the top of the file
import warnings
warnings.filterwarnings("ignore", category=DeprecationWarning)

import sys
import os
from .utils import resource_path, external_data_path

# Application Constants
APP_NAME = "SnapTrace"
APP_ICON = resource_path(os.path.join("assets", "logo.png"))
DEFECT_CSV = external_data_path("defect_feedbacks.csv")  # External file next to executable

# Icons directory path
ICONS_DIR = resource_path(os.path.join("assets", "icons"))

# Default settings
DEFAULT_PEN_SIZE = 2
DEFAULT_COUNTER_START = 1
MAX_UNDO_STATES = 50
DEFAULT_FONT_SIZE = 12
