# -*- coding: utf-8 -*-

"""
REST API
"""

from configparser import ConfigParser
from os import environ

from bottle import get, post, request, run

import video_contrast_analysis.globals as globals
from video_contrast_analysis import __version__
from video_contrast_analysis.analysis import video_contrast_analysis


@get("/api/py")
def version():
    """
    Set [global] config from request body and store to disk

    :return: dict with key "config_written_to" with path to config file
    :rtype: ```dict```
    """
    config_s = request.body.read().decode("utf-8")
    with open(globals.CONFIG_FILEPATH, "wt") as f:
        f.write(config_s)

    globals.CONFIG = ConfigParser()
    globals.CONFIG.read_string(config_s)

    return {"version": __version__}


@post("/api/py/set_config")
def set_config_route():
    """
    Set [global] config from request body and store to disk

    :return: dict with key "config_written_to" with path to config file
    :rtype: ```dict```
    """
    config_s = request.body.read().decode("utf-8")
    with open(globals.CONFIG_FILEPATH, "wt") as f:
        f.write(config_s)

    globals.CONFIG = ConfigParser()
    globals.CONFIG.read_string(config_s)

    return {"config_written_to": globals.CONFIG_FILEPATH}


if __name__ == "__main__":
    host = environ.get("SERVER_HOST", "0.0.0.0")
    port = int(environ.get("SERVER_PORT", "80"))
    print("Running on {}:{}".format(host, port))
    run(host=host, port=port)
    
