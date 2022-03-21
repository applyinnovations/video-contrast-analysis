# -*- coding: utf-8 -*-
from configparser import ConfigParser

from video_contrast_analysis import CONFIG_FILEPATH


def get_config():
    """
    Get parsed config from file or None if nonexistent

    :return: ConfigParser or None
    :rtype: ```Optional[ConfigParser]```
    """
    config = ConfigParser()
    with open(CONFIG_FILEPATH, "rt") as f:
        config.read_file(f, CONFIG_FILEPATH)
    return config


__all__ = ["get_config"]
