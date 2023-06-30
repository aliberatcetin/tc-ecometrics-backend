import warnings

import pandas as pd
from kink import di

from file_manager import FileManager

warnings.simplefilter(action="ignore", category=FutureWarning)
pd.options.mode.chained_assignment = None  # default='warn'


def initialize_context():
    di[FileManager] = FileManager()

    return di
