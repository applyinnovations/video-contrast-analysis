# -*- coding: utf-8 -*-

"""
Utility functions
"""

from configparser import ConfigParser
from os import path
from pprint import PrettyPrinter


def get_config(config_filepath):
    """
    Get parsed config from file or None if nonexistent

    :param config_filepath: config filepath
    :type config_filepath: ```str```

    :return: ConfigParser or None
    :rtype: ```Optional[ConfigParser]```
    """
    if not path.isfile(config_filepath):
        return None
    config = ConfigParser()
    with open(config_filepath, "rt") as f:
        config.read_file(f, config_filepath)
    return config


pp = PrettyPrinter(indent=4).pprint

__all__ = ["get_config", "pp"]
