#!/usr/bin/env python
# -*- coding: utf-8 -*-

from os import environ, getcwd, path

__author__ = "Alex Bunn & Samuel Marks"
__version__ = "0.0.1"

from video_contrast_analysis.utils import get_config

CONFIG_FILEPATH = environ.get("CONFIG_FILEPATH", path.join(getcwd(), "config.ini"))
CONFIG = get_config()

__all__ = ["CONFIG_FILEPATH", "CONFIG", "__author__", "__version__"]
