# -*- coding: utf-8 -*-
"""
Global variables
"""

from os import environ, getcwd, path

from video_contrast_analysis.utils import get_config

CONFIG_FILEPATH = environ.get("CONFIG_FILEPATH", path.join(getcwd(), "config.ini"))
CONFIG = get_config(CONFIG_FILEPATH)

__all__ = ["CONFIG_FILEPATH", "CONFIG"]
