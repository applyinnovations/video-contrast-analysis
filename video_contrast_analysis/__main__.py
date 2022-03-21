#!/usr/bin/env python
# -*- coding: utf-8 -*-

from argparse import ArgumentParser

from video_contrast_analysis import __author__, __version__
from video_contrast_analysis.analysis import video_contrast_analysis


def _build_parser():
    """
    Build argparse parser object

    :returns argparse parser object
    :rtype ArgumentParser
    """
    parser = ArgumentParser(description='Run video contrast analysis on `--input-video` writing to `--output-srt`')
    parser.add_argument('-i', '--input-video', help='Filepath to video_file (in format supported by OpenCV)', required=True, dest='video_file')
    parser.add_argument('-o', '--output-srt', help='Filepath to write subtitles to (in SRT format)', required=True, dest='subtitle_file')
    return parser


if __name__ == '__main__':
    video_contrast_analysis(**dict(_build_parser().parse_args()._get_kwargs()))
