# -*- coding: utf-8 -*-

"""
REST API
"""

from configparser import ConfigParser
from os import environ

from bottle import post, request, run

import video_contrast_analysis.globals as globals
from video_contrast_analysis.analysis import video_contrast_analysis


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


@post("/api/py/analyse/<video_file>/<subtitle_file>")
def analysis_route(video_file, subtitle_file):
    """
    Run analysis using URL path as arguments

    :param video_file: Filepath to video_file (in format supported by OpenCV)
    :type video_file: ```str```

    :param subtitle_file: Filepath to write subtitles to in SRT format
    :type subtitle_file: ```str```

    :return: `{"video_analysed": True}`
    :rtype: ```dict```
    """
    video_contrast_analysis(video_file=video_file, subtitle_file=subtitle_file)

    return {"video_analysed": True}


if __name__ == "__main__":
    run(
        host=environ.get("SERVER_HOST", "localhost"),
        port=int(environ.get("SERVER_PORT", "8080")),
    )
